import boto3
import typer
from os import getenv
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# .env ფაილის ჩატვირთვა შენი AWS კონფიგურაციით
load_dotenv()

app = typer.Typer(help="S3 Versioning Management CLI Tool")

def get_s3_client():
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
    file: str = typer.Option(None, "--file", "-f", help="ფაილის სახელი (Key)"),
    status: bool = typer.Option(False, "--status", "-s", help="აჩვენებს Versioning-ის სტატუსს"),
    enable: bool = typer.Option(False, "--enable", help="ჩართავს Versioning-ს ბაკეტზე"),
    versions: bool = typer.Option(False, "--versions", "-v", help="აჩვენებს ფაილის ვერსიების რაოდენობას და თარიღებს"),
    rollback: bool = typer.Option(False, "--rollback", "-r", help="ბოლოს წინა ვერსიის ატვირთვა ახალ ვერსიად")
):
    """
    დავალება: S3 ბაკეტის ვერსიონირების მართვა.
    """
    try:
        # 1. Versioning-ის ჩართვა (საჭიროა, რომ ვერსიები საერთოდ შეიქმნას)
        if enable:
            s3_client.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            typer.echo(f"✅ წარმატება: ვერსიონირება ჩაირთო ბაკეტზე '{bucket}'.")

        # 2. სტატუსის ჩვენება
        if status:
            res = s3_client.get_bucket_versioning(Bucket=bucket)
            current_status = res.get('Status', 'Disabled')
            typer.echo(f"🔍 ბაკეტის '{bucket}' ვერსიონირების სტატუსი: {current_status}")

        # 3. ვერსიების სია (რაოდენობა და თარიღები)
        if versions:
            if not file:
                typer.echo("❌ შეცდომა: მიუთითეთ ფაილის სახელი --file ფლაგით.")
                return
            
            res = s3_client.list_object_versions(Bucket=bucket, Prefix=file)
            all_versions = [v for v in res.get('Versions', []) if v['Key'] == file]
            
            if not all_versions:
                typer.echo(f"❌ ფაილის '{file}' ვერსიები ვერ მოიძებნა.")
            else:
                typer.echo(f"📊 ფაილს '{file}' აქვს {len(all_versions)} ვერსია:")
                for v in all_versions:
                    is_latest = "(Latest)" if v['IsLatest'] else ""
                    typer.echo(f"  - Date: {v['LastModified']} | ID: {v['VersionId'][:12]}... {is_latest}")

        # 4. Rollback (ბოლოს წინა ვერსიის Promote)
        if rollback:
            if not file:
                typer.echo("❌ შეცდომა: მიუთითეთ ფაილის სახელი --file ფლაგით.")
                return

            res = s3_client.list_object_versions(Bucket=bucket, Prefix=file)
            all_versions = [v for v in res.get('Versions', []) if v['Key'] == file]

            if len(all_versions) < 2:
                typer.echo("⚠️ ბოლოს წინა ვერსია არ არსებობს (საჭიროა მინიმუმ 2 ვერსია).")
            else:
                # ინდექსი 1 არის ბოლოს წინა ვერსია
                prev_id = all_versions[1]['VersionId']
                
                s3_client.copy_object(
                    Bucket=bucket,
                    Key=file,
                    CopySource={'Bucket': bucket, 'Key': file, 'VersionId': prev_id}
                )
                typer.echo(f"✅ წარმატება: ბოლოს წინა ვერსია ({prev_id[:12]}...) აიტვირთა ახალ ვერსიად.")

    except ClientError as e:
        typer.echo(f"❌ AWS შეცდომა: {e}")
    except Exception as e:
        typer.echo(f"❌ შეცდომა: {e}")

if __name__ == "__main__":
    app()
    