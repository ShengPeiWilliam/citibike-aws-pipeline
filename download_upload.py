import boto3
import requests
import os
import zipfile

BUCKET = "citibike-pipeline-william-842549706992-us-east-1-an"
BASE_URL = "https://s3.amazonaws.com/tripdata"

s3 = boto3.client("s3", region_name="us-east-1")

def download_and_upload(year, month):
    month_str = str(month).zfill(2)
    zip_filename = f"JC-{year}{month_str}-citibike-tripdata.csv.zip"
    csv_filename = f"JC-{year}{month_str}-citibike-tripdata.csv"
    url = f"{BASE_URL}/{zip_filename}"
    local_zip = f"/tmp/{zip_filename}"
    local_csv = f"/tmp/{csv_filename}"

    print(f"Downloading {zip_filename}...")
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed: {url}")
        return

    with open(local_zip, "wb") as f:
        f.write(r.content)

    print(f"Unzipping...")
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall("/tmp/")

    s3_key = f"raw/year={year}/month={month_str}/{csv_filename}"
    print(f"Uploading to s3://{BUCKET}/{s3_key}...")
    s3.upload_file(local_csv, BUCKET, s3_key)

    os.remove(local_zip)
    os.remove(local_csv)
    print(f"Done: {csv_filename}")

if __name__ == "__main__":
    for month in range(2, 10):
        download_and_upload(2024, month)