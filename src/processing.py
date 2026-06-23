import boto3
import io
import os
import pandas as pd
import holidays

BUCKET = "citibike-pipeline-william-842549706992-us-east-1-an"

s3 = boto3.client("s3", region_name="us-east-1")

def read_csv_from_s3(key):
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()))

def upload_csv_to_s3(df, key):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())

def get_season(month):
    if month in [12, 1, 2]:
        return 1  # winter
    elif month in [3, 4, 5]:
        return 2  # spring
    elif month in [6, 7, 8]:
        return 3  # summer
    else:
        return 4  # fall

def process(year, month):
    month_str = str(month).zfill(2)
    print(f"Processing {year}-{month_str}...")

    # load citibike
    citibike_key = f"raw/citibike/year={year}/month={month_str}/JC-{year}{month_str}-citibike-tripdata.csv"
    citibike = read_csv_from_s3(citibike_key)
    citibike["date"] = pd.to_datetime(citibike["started_at"]).dt.date.astype(str)

    daily = citibike.groupby("date").agg(
        total_rides=("ride_id", "count"),
        member_count=("member_casual", lambda x: (x == "member").sum()),
        casual_count=("member_casual", lambda x: (x == "casual").sum()),
    ).reset_index()

    # load weather
    weather_key = f"raw/weather/year={year}/month={month_str}/weather.csv"
    weather = read_csv_from_s3(weather_key)
    weather = weather.drop(columns=["temp_mean"])

    # join
    merged = daily.merge(weather, on="date", how="inner")

    # derive date features
    us_holidays = holidays.US(state="NJ", years=year)
    merged["date"] = pd.to_datetime(merged["date"])
    merged["yr"] = merged["date"].dt.year
    merged["mnth"] = merged["date"].dt.month
    merged["season"] = merged["mnth"].apply(get_season)
    merged["weekday"] = merged["date"].dt.weekday  # 0=Monday, 6=Sunday
    merged["workingday"] = merged["weekday"].apply(lambda x: 1 if x < 5 else 0)
    merged["holiday"] = merged["date"].apply(lambda x: 1 if x in us_holidays else 0)
    merged["date"] = merged["date"].astype(str)

    # upload
    out_key = f"processed/year={year}/month={month_str}/merged.csv"
    upload_csv_to_s3(merged, out_key)
    print(f"Done: s3://{BUCKET}/{out_key}")

if __name__ == "__main__":
    for year in range(2022, 2025):
        for month in range(1, 13):
            process(year, month)
