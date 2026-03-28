import boto3
import typer
import os
from dotenv import load_dotenv
from collections import Counter
from botocore.exceptions import ClientError

# .env ფაილის ჩატვირთვა
load_dotenv(".env")

app = typer.Typer(help="S3 File Organizer - დავალება: ფაილების დაჯგუფება გაფართოების მიხედვით")

def get_s3_client():
    """AWS კლიენტის ინიციალიზაცია .env ცვლადებით"""
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
        aws_session_token=os.getenv("aws_session_token"),
        region_name=os.getenv("aws_region_name", "us-east-1")
    )

s3 = get_s3_client()

@app.command()
def organize(bucket: str = typer.Argument(..., help="S3 Bucket-ის სახელი")):
    """
    ამოწმებს თითოეული ფაილის გაფართოებას და გადააქვს შესაბამის ფოლდერში.
    """
    try:
        # 1. ბაკეტში არსებული ობიექტების წაკითხვა
        response = s3.list_objects_v2(Bucket=bucket)
        
        if 'Contents' not in response:
            typer.echo(f"📭 ბაკეტი '{bucket}' ცარიელია.")
            return

        # ოპერაციების დასათვლელი (Counter)
        stats = Counter()

        for obj in response['Contents']:
            old_key = obj['Key']
            
            # გამოვტოვოთ ფოლდერები და ის ფაილები, რომლებიც უკვე დალაგებულია (შეცავს / სიმბოლოს)
            if old_key.endswith('/') or '/' in old_key:
                continue

            # 2. გაფართოების დადგენა (მაგ: image.jpg -> jpg)
            parts = old_key.split('.')
            if len(parts) > 1:
                extension = parts[-1].lower()
                new_key = f"{extension}/{old_key}"

                # 3. ფაილის გადატანა (კოპირება + წაშლა)
                # S3-ში გადატანა ხდება ჯერ კოპირებით ახალ პათზე
                s3.copy_object(
                    Bucket=bucket,
                    CopySource={'Bucket': bucket, 'Key': old_key},
                    Key=new_key
                )
                
                # შემდეგ ძველი ობიექტის წაშლით
                s3.delete_object(Bucket=bucket, Key=old_key)
                
                # სტატისტიკის განახლება
                stats[extension] += 1
                typer.echo(f"✅ Moved: {old_key} -> {new_key}")

        # 4. შედეგების დაბეჭდვა დავალების ფორმატით
        typer.echo("\n📊 ოპერაციების რაოდენობა:")
        if not stats:
            typer.echo("დასამუშავებელი ფაილები არ მოიძებნა.")
        else:
            for ext, count in stats.items():
                typer.echo(f"{ext} - {count}")

    except ClientError as e:
        typer.echo(f"❌ AWS Error: {e}")
    except Exception as e:
        typer.echo(f"❌ მოულოდნელი შეცდომა: {e}")

if __name__ == "__main__":
    app()
