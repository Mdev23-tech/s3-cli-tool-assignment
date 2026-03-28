import boto3
import json
import magic
import io
import logging
import typer
from os import getenv
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from urllib.request import urlopen
from hashlib import md5
from time import localtime

# Logging კონფიგურაცია
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
app = typer.Typer(help="კომფორტული S3 Bucket CLI ხელსაწყო")

def init_client():
    """S3 კლიენტის ინიციალიზაცია და ავტორიზაციის შემოწმება"""
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=getenv("aws_access_key_id"),
            aws_secret_access_key=getenv("aws_secret_access_key"),
            aws_session_token=getenv("aws_session_token"),
            region_name=getenv("aws_region_name")
        )
        client.list_buckets() # შემოწმება
        return client
    except ClientError as e:
        logger.error(f"ავტორიზაციის შეცდომა: {e}")
        raise typer.Exit(code=1)

s3_client = init_client()

@app.command()
def list_buckets():
    """ყველა ბაკეტის ჩამონათვალი"""
    response = s3_client.list_buckets()
    for b in response.get('Buckets', []):
        print(f" - {b['Name']}")

@app.command()
def create_bucket(name: str, region: str = "us-west-2"):
    """ახალი ბაკეტის შექმნა"""
    try:
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=name, CreateBucketConfiguration=location)
        logger.info(f"ბაკეტი '{name}' წარმატებით შეიქმნა.")
    except ClientError as e:
        logger.error(e)

@app.command()
def delete_bucket(name: str):
    """ბაკეტის წაშლა"""
    try:
        s3_client.delete_bucket(Bucket=name)
        logger.info(f"ბაკეტი '{name}' წაიშალა.")
    except ClientError as e:
        logger.error(e)

@app.command()
def bucket_exists(name: str):
    """ბაკეტის არსებობის შემოწმება"""
    try:
        s3_client.head_bucket(Bucket=name)
        print(f"ბაკეტი '{name}' არსებობს: True")
    except ClientError:
        print(f"ბაკეტი '{name}' არსებობს: False")

@app.command()
def download_and_upload(bucket: str, url: str, keep_local: bool = False):
    """ფაილის ატვირთვა MIME ვალიდაციით (.bmp, .jpg, .jpeg, .png, .webp, .mp4)"""
    allowed_mimes = [
        'image/bmp', 'image/jpeg', 'image/png', 
        'image/webp', 'video/mp4'
    ]
    
    # ავტომატური სახელის გენერაცია md5-ით (როგორც source code-ში იყო)
    file_name = f'file_{md5(str(localtime()).encode("utf-8")).hexdigest()}'
    
    try:
        with urlopen(url) as res:
            content = res.read()
            # MIME ტიპის დადგენა ბაიტებით
            mimetype = magic.Magic(mime=True).from_buffer(content)
            
            if mimetype not in allowed_mimes:
                logger.error(f"აკრძალული ფორმატი: {mimetype}")
                return
            
            # გაფართოების დამატება მოდულიდან გამომდინარე
            ext = mimetype.split('/')[-1]
            final_name = f"{file_name}.{ext}"

            s3_client.upload_fileobj(
                io.BytesIO(content), 
                bucket, 
                final_name, 
                ExtraArgs={'ContentType': mimetype}
            )
            logger.info(f"აიტვირთა წარმატებით! ტიპი: {mimetype}, სახელი: {final_name}")
            
            if keep_local:
                with open(final_name, 'wb') as f:
                    f.write(content)
    except Exception as e:
        logger.error(f"შეცდომა: {e}")

@app.command()
def set_policy(bucket: str):
    """ბაკეტის საჯარო წვდომის პოლიტიკის შექმნა (Block მოხსნით)"""
    try:
        # Permission პრობლემის მოგვარება (წყარო: slide code)
        s3_client.delete_public_access_block(Bucket=bucket)
        
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket}/*",
            }]
        }
        s3_client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
        print("ბაკეტის პოლიტიკა წარმატებით შეიქმნა.")
    except ClientError as e:
        logger.error(e)

@app.command()
def read_policy(bucket: str):
    """ბაკეტის პოლიტიკის წაკითხვა"""
    try:
        policy = s3_client.get_bucket_policy(Bucket=bucket)
        print(policy["Policy"])
    except ClientError as e:
        logger.error(e)

if __name__ == "__main__":
    app()
    