# AWS S3 CLI Utility

A command-line interface tool built with Python for managing Amazon S3 resources. This project implements secure bucket operations, automated MIME-type validation, and bucket policy management.

## Technical Stack

* **Dependency Management**: [Poetry](https://python-poetry.org/)
* **CLI Framework**: [Typer](https://typer.tiangolo.com/)
* **AWS SDK**: [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* **Validation**: [python-magic](https://pypi.org/project/python-magic/) for byte-level MIME detection.

## Core Features

* **Secure File Transfer**: Integrated `download-and-upload` functionality with:
    * **MIME Validation**: Restricts uploads to `.bmp, .jpg, .jpeg, .png, .webp, .mp4`.
    * **Automated Naming**: Collision-resistant file naming via MD5 hashing.
* **Policy Management**: 
    * Automatic removal of Public Access Blocks.
    * Programmatic S3 Bucket Policy generation and deployment.
      
## Installation & Setup

1. **Clone & Install**:
   ```bash
   git clone [https://github.com/Mdev23-tech/s3-cli-tool-assignment.git](https://github.com/Mdev23-tech/s3-cli-tool-assignment.git)
   cd s3-cli-tool-assignment
   poetry install

Usage Guide
General Operations
List Buckets: poetry run s3-tool list-buckets

Create Bucket: poetry run s3-tool create-bucket <name>

Verify Existence: poetry run s3-tool bucket-exists <name>

Delete Bucket: poetry run s3-tool delete-bucket <name>

Security & Uploads
Upload with Validation: poetry run s3-tool download-and-upload <bucket> <url>

Apply Public Policy: poetry run s3-tool set-policy <bucket>

Read Policy: poetry run s3-tool read-policy <bucket>
