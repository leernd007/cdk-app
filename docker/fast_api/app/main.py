import boto3
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
app = FastAPI()

# @app.get("/")
# def read_root():
#     # HTML_FILE_PATH = "index.html"
#     # with open(HTML_FILE_PATH, "r", encoding="utf-8") as file:
#     #     html_content = file.read()
#     # return Response(content=html_content, media_type="text/html")
#     s3 = boto3.client('s3')
#
#     bucket_name = "simple-andrii-web-app"
#     file_key = "index.html"
#
#     response = s3.get_object(Bucket=bucket_name, Key=file_key)
#
#     html_content  = response['Body'].read().decode('utf-8')
#
#     return Response(content=html_content, media_type="text/html")


@app.get("/api")
def api():
    # return {'Hello': 'World'}
    s3_client = boto3.client('s3', region_name="us-east-1")

    bucket_name = 'andriis-sftp-files'
    # bucket_name = os.environ['BUCKET_NAME']
    response = s3_client.list_objects_v2(Bucket=bucket_name)

    files = {}
    i = 0
    for item in response["Contents"]:
        files[i] = item['Key']
        i = i+1

    return files