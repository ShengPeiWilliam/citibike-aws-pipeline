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
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print(f"Failed: {url}")
        return

    with open(local_zip, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Unzipping...")
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall("/tmp/")
        extracted_name = z.namelist()[0]
    local_csv = f"/tmp/{extracted_name}"

    s3_key = f"raw/citibike/year={year}/month={month_str}/{extracted_name}"
    print(f"Uploading to s3://{BUCKET}/{s3_key}...")
    try:
        s3.upload_file(local_csv, BUCKET, s3_key)
    finally:
        if os.path.exists(local_zip):
            os.remove(local_zip)
        if os.path.exists(local_csv):
            os.remove(local_csv)
    print(f"Done: {extracted_name}")

if __name__ == "__main__":
    for month in range(1, 13):
        download_and_upload(2024, month)