"""
Run from backend/ with .venv active:
    python -m scripts.upload_service_report
"""

import asyncio
import boto3

from app.database import AsyncSessionLocal
from app.models import ServiceReport

BUCKET_NAME = "robopulse-diagnostics-nd2478" # Yes, it is correctly named robopulse (reusing)
LOCAL_FILE_PATH = "scripts/sample_service_report.txt"
#the s3 key is just a path within the s3 bucket where the file will be stored
S3_KEY = "diagnostics/rx1001-003.txt" # Yes, correctly named

#a function to upload the file to the s3 bucket and return the s3 url
def upload_to_s3() -> str:
    s3_client = boto3.client("s3")
    s3_client.upload_file(LOCAL_FILE_PATH, BUCKET_NAME, S3_KEY)
    return f"s3://{BUCKET_NAME}/{S3_KEY}"

#async function to record the report in the database
async def record_service_report(file_url: str) -> None:
    async with AsyncSessionLocal() as session:
        log = ServiceReport(
            field_job_id=1,
            file_url=file_url,
            notes="Uploaded via the boto3 demo script.",
        )

        session.add(log)
        await session.commit()
        await session.refresh(log)
        print(f"Created ServiceReport id={log.id}, file_url={log.file_url}")

#async main function to run the uplaod and record the log
async def main() -> None:
    file_url = upload_to_s3()
    print(f"Uploaded to {file_url}")
    await record_service_report(file_url)

if __name__ == "__main__":
    asyncio.run(main())