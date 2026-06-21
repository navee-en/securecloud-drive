import boto3
from config import Config

s3 = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.S3_REGION
)


def upload_file_to_s3(file, filename):
    s3.upload_fileobj(
        file,
        Config.S3_BUCKET,
        filename
    )


def get_file_url(filename):
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": Config.S3_BUCKET,
            "Key": filename
        },
        ExpiresIn=3600
    )


def delete_file_from_s3(filename):
    s3.delete_object(
        Bucket=Config.S3_BUCKET,
        Key=filename
    )