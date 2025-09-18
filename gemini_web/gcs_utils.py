import os
import pandas as pd
from google.cloud import storage, bigquery

# 환경 변수에 JSON 키 파일 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./config/codeit-project-567b5092fd38.json"

# GCS 클라이언트 및 BigQuery 클라이언트 초기화
storage_client = storage.Client()
bigquery_client = bigquery.Client()

def download_csv_from_gcs(bucket_name, prefix):
    """
    GCS에서 파일 다운로드 및 병합.
    :param bucket_name: GCS 버킷 이름
    :param prefix: 다운로드할 경로 (GCS 버킷 내부 폴더)
    :return: 파일별 데이터프레임 딕셔너리 (key: 파일 이름, value: 데이터프레임)
    """
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)  # 지정된 경로의 파일 검색
    dataframes = {}  # 파일별 데이터프레임 저장
    file_names = []

    for blob in blobs:
        if blob.name.endswith(".csv"):
            file_name = blob.name.split("/")[-1].replace(".csv", "")  # 파일 이름 추출
            print(f"Downloading: {blob.name}")
            # GCS에서 바로 메모리로 읽기
            with blob.open("rb") as file:
                df = pd.read_csv(file, engine="pyarrow")
                dataframes[file_name] = df
                file_names.append(file_name)

    if not dataframes:
        print(f"No Parquet files found at prefix: {prefix}")
    return dataframes, file_names  # 파일 이름별 데이터프레임 딕셔너리 반환
