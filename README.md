# AWS S3 CLI Utility

A command-line interface tool built with Python for managing Amazon S3 resources. This project implements secure bucket operations, automated MIME-type validation, and bucket policy management.

## Technical Stack

* **Dependency Management**: [Poetry](https://python-poetry.org/)
* **CLI Framework**: [Typer](https://typer.tiangolo.com/)
* **AWS SDK**: [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/)
* **Validation**: [python-magic](https://pypi.org/project/python-magic/) for byte-level MIME detection.

## Core Features

* **Secure File Transfer**: 
    * **MIME Validation**: Restricts uploads to `.bmp, .jpg, .jpeg, .png, .webp, .mp4, .pdf`.
    * **Automated Naming**: Collision-resistant file naming via MD5 hashing.
* **Policy & Lifecycle Management**: 
    * Automatic removal of Public Access Blocks.
    * Programmatic S3 Bucket Policy generation and deployment.
    * **Assignment 4 Enhancements**:
        * **Multipart Upload**: Handles large files (threshold: 20MB) using `TransferConfig` for stability.
        * **Lifecycle Management**: Automated 120-day object expiration policy.

## Installation & Setup

1. **Clone & Install**:
   ```bash
   git clone [https://github.com/Mdev23-tech/s3-cli-tool-assignment.git](https://github.com/Mdev23-tech/s3-cli-tool-assignment.git)
   cd s3-cli-tool-assignment
   poetry install

2.   Environment Variables:
Create a .env file and add your AWS credentials:

aws_access_key_id=YOUR_KEY
aws_secret_access_key=YOUR_SECRET
aws_session_token=YOUR_TOKEN
aws_region_name=YOUR_REGION

Usage Guide
General Operations
List Buckets: poetry run s3-tool list-buckets

Create Bucket: poetry run s3-tool create-bucket <name>

Verify Existence: poetry run s3-tool bucket-exists <name>

Delete Bucket: poetry run s3-tool delete-bucket <name>

Uploads & Validation
Remote Download & Upload:
poetry run s3-tool download-and-upload <bucket> <url>

Local File Upload (with Multipart & MIME check):
poetry run s3-tool upload-file <bucket-name> <local-file-path>

Policy & Lifecycle Management
Apply Public Policy: poetry run s3-tool set-policy <bucket>

Read Policy: poetry run s3-tool read-policy <bucket>

Configure Lifecycle (120-Day Expiration):
poetry run s3-tool set-lifecycle <bucket-name>


