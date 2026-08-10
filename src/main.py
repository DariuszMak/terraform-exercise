import logging
from pathlib import Path

from src.env_loader import load_dev_env
from src.s3_client import S3Client as S3Client

logger = logging.getLogger(__name__)


def run() -> None:
    load_dev_env()
    client = S3Client.from_env()

    if not client.bucket_exists():
        logger.error(
            "Bucket %s does not exist, run 'task localstack-terraform' first",
            client.bucket_name,
        )
        return

    sample_file = Path("test.txt")
    sample_file.write_text("Hello from LocalStack S3\n", encoding="utf-8")

    client.upload_file(sample_file, sample_file.name)
    keys = client.list_objects()
    logger.info("Objects in bucket %s: %s", client.bucket_name, keys)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
