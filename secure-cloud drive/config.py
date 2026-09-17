import os 
class Config:
    SECRET_KEY = "your-secret-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "uploads"

    S3_BUCKET = "secure-cloud-drive-navee"
    S3_REGION = "ap-south-1"

    AWS_ACCESS_KEY_ID = ("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = ("AWS_SECRET_ACCESS_KEY")

    GOOGLE_CLIENT_ID = ("YOUR_CILENT_ID")
    GOOGLE_CLIENT_SECRET = ("YOUR_CILENT_SECRET")
