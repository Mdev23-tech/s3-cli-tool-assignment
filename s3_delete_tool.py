import boto3
import typer
from os import getenv
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# .env ფაილის ჩატვირთვა (გამოიყენებს შენს არსებულ AWS გასაღებებს)
load_dotenv()

app = typer.Typer(help="S3 Object Management Tool")

def get_s3_client():
    """S3 კლიენტის ინიციალიზაცია"""
    return boto3.client(
        "s3",
        aws_access_key_id=getenv("aws_access_key_id"),
        aws_secret_access_key=getenv("aws_secret_access_key"),
        aws_session_token=getenv("aws_session_token"),
        region_name=getenv("aws_region_name")
    )

s3_client = get_s3_client()

@app.command()
def manage(
    bucket: str = typer.Argument(..., help="Bucket-ის სახელი"),
    key: str = typer.Argument(..., help="ფაილის სახელი (Object Key)"),
    delete: bool = typer.Option(
        False, 
        "--del", 
        help="მიუთითეთ ეს ფლაგი ფაილის წასაშლელად"
    )
):
    """
    დავალება: ობიექტის მართვა ბაკეტში. 
    თუ მითითებულია --del ფლაგი, ობიექტი წაიშლება.
    """
    if delete:
        try:
            # ჯერ ვამოწმებთ არსებობს თუ არა ობიექტი
            s3_client.head_object(Bucket=bucket, Key=key)
            
            # წაშლის პროცესი
            s3_client.delete_object(Bucket=bucket, Key=key)
            print(f"✅ წარმატება: ობიექტი '{key}' წაიშალა ბაკეტიდან '{bucket}'.")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == "404":
                print(f"❌ შეცდომა: ობიექტი '{key}' ვერ მოიძებნა ბაკეტში '{bucket}'.")
            else:
                print(f"❌ შეცდომა: {e}")
    else:
        print(f"ℹ️ პარამეტრები მიღებულია: Bucket='{bucket}', Key='{key}'.")
        print("💡 ფაილის წასაშლელად დაამატეთ ფლაგი: --del")

if __name__ == "__main__":
    app()
    