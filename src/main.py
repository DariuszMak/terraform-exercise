import logging
from pathlib import Path

from src.env_loader import load_dev_env
from src.s3_client import S3Client

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

    sample_file_1 = Path("test.txt")
    sample_file_1.write_text("Hello from LocalStack S3 - File 1\n", encoding="utf-8")

    sample_file_2 = Path("test_batch.txt")
    sample_file_2.write_text("Hello from LocalStack S3 - File 2\n", encoding="utf-8")

    file_checksum = client.upload_file(sample_file_1, sample_file_1.name, metadata={"author": "dev-team"})
    logger.info("Uploaded %s with SHA256 checksum: %s", sample_file_1.name, file_checksum)

    batch_pairs = [(sample_file_2, "batch/test_batch.txt")]
    client.upload_batch(batch_pairs)

    metadata = client.get_object_metadata(sample_file_1.name)
    logger.info("Fetched metadata for %s: %s", sample_file_1.name, metadata)

    presigned_url = client.generate_presigned_url(sample_file_1.name, expiration=1800)
    logger.info("Generated Presigned URL: %s", presigned_url)

    client.copy_object(sample_file_1.name, "backups/test_backup.txt")

    keys = client.list_objects()
    logger.info("All objects in bucket %s: %s", client.bucket_name, keys)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
