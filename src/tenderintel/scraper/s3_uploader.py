import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET")

# Initialize S3 client only if credentials are available
s3 = None
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY)
        print("✅ AWS S3 client initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize S3 client: {e}")
else:
    print("⚠️ AWS credentials not found in .env - S3 upload features disabled")

def upload_to_s3(file_path, tender_id):
    """Upload file to S3 (optional - requires .env configuration)"""
    if not s3 or not BUCKET_NAME:
        print("⚠️ S3 not configured - skipping file upload")
        return None
        
    file_name = f"{tender_id}.zip"
    try:
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        print(f"✅ Uploaded to S3: {s3_url}")
        return s3_url
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except NoCredentialsError:
        print("❌ AWS credentials not available")
        return None
    except Exception as e:
        print(f"❌ S3 upload error: {e}")
        return None
