import boto3
import requests
import csv
import os
import calendar

BUCKET = "citibike-pipeline-william-842549706992-us-east-1-an"

s3 = boto3.client("s3", region_name="us-east-1")

def fetch_and_upload(year, month):
    month_str = str(month).zfill(2)
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}-{month_str}-01"
    end = f"{year}-{month_str}-{last_day}"

    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "start_date": start,
        "end_date": end,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "apparent_temperature_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "weathercode",
            "relative_humidity_2m_mean",
        ]),
        "timezone": "America/New_York",
    }

    print(f"Fetching weather {year}-{month_str}...")
    r = requests.get("https://historical-forecast-api.open-meteo.com/v1/forecast", params=params)
    if r.status_code != 200:
        print(f"Failed: {r.status_code} {r.text}")
        return

    daily = r.json()["daily"]
    dates = daily["time"]

    local_csv = f"/tmp/weather_{year}{month_str}.csv"
    with open(local_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date", "temp_max", "temp_min", "temp_mean",
            "atemp_mean", "precipitation", "windspeed_max",
            "weathercode", "humidity_mean",
        ])
        for i, date in enumerate(dates):
            writer.writerow([
                date,
                daily["temperature_2m_max"][i],
                daily["temperature_2m_min"][i],
                daily["temperature_2m_mean"][i],
                daily["apparent_temperature_mean"][i],
                daily["precipitation_sum"][i],
                daily["windspeed_10m_max"][i],
                daily["weathercode"][i],
                daily["relative_humidity_2m_mean"][i],
            ])

    s3_key = f"raw/weather/year={year}/month={month_str}/weather.csv"
    print(f"Uploading to s3://{BUCKET}/{s3_key}...")
    try:
        s3.upload_file(local_csv, BUCKET, s3_key)
    finally:
        if os.path.exists(local_csv):
            os.remove(local_csv)
    print(f"Done: {year}-{month_str}")

if __name__ == "__main__":
    for year in range(2022, 2025):
        for month in range(1, 13):
            fetch_and_upload(year, month)
