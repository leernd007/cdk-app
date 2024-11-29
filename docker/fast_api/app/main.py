import boto3
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api")
def api():
    s3_client = boto3.client('s3', region_name="us-east-1")

    bucket_name = 'andriis-sftp-files'

    response = s3_client.list_objects_v2(Bucket=bucket_name)

    files = {}
    i = 0
    for item in response["Contents"]:
        files[i] = item['Key']
        i = i+1

    return files