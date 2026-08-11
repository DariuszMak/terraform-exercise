from __future__ import annotations

import hashlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class S3Settings:
    bucket_name: str
    endpoint_url: str
    region_name: str
    access_key_id: str
    secret_access_key: str

    @classmethod
    def from_env(cls) -> S3Settings:
        return cls(
            bucket_name=os.environ.get("S3_BUCKET_NAME", "terraform-localstack-demo"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "eu-west-1"),
            access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )


class S3Client:
    def __init__(self, settings: S3Settings) -> None:
        self._settings = settings
        client_kwargs: dict[str, Any] = {
            "region_name": settings.region_name,
            "aws_access_key_id": settings.access_key_id,
            "aws_secret_access_key": settings.secret_access_key,
            "config": Config(
                s3={"addressing_style": "path"},
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        }
        if settings.endpoint_url:
            client_kwargs["endpoint_url"] = settings.endpoint_url
        self._client = boto3.client("s3", **client_kwargs)

    @classmethod
    def from_env(cls) -> S3Client:
        return cls(S3Settings.from_env())

    @property
    def bucket_name(self) -> str:
        return self._settings.bucket_name

    def bucket_exists(self) -> bool:
        try:
            self._client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            return False
        return True

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with file_path.open("rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def upload_file(
        self,
        local_path: Path,
        key: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        file_hash = self.calculate_sha256(local_path)
        meta = metadata.copy() if metadata else {}
        meta["sha256"] = file_hash

        logger.info("Uploading %s to s3://%s/%s with hash %s", local_path, self.bucket_name, key, file_hash)
        self._client.upload_file(
            str(local_path),
            self.bucket_name,
            key,
            ExtraArgs={"Metadata": meta},
        )
        return file_hash

    def upload_batch(self, file_key_pairs: list[tuple[Path, str]], max_workers: int = 4) -> list[str]:
        results: list[str] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.upload_file, path, key): key for path, key in file_key_pairs}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    file_hash = future.result()
                    results.append(file_hash)
                    logger.info("Batch upload succeeded for key: %s", key)
                except Exception as exc:
                    logger.exception("Batch upload failed for key %s: %s", key, exc)
                    raise
        return results

    def download_file(self, key: str, local_path: Path) -> None:
        logger.info("Downloading s3://%s/%s to %s", self.bucket_name, key, local_path)
        self._client.download_file(self.bucket_name, key, str(local_path))

    def list_objects(self, prefix: str = "") -> list[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            keys.extend(obj["Key"] for obj in page.get("Contents", []))
        logger.info("Listed %d object(s) in s3://%s", len(keys), self.bucket_name)
        return keys

    def get_object_metadata(self, key: str) -> dict[str, Any]:
        logger.info("Fetching metadata for s3://%s/%s", self.bucket_name, key)
        response = self._client.head_object(Bucket=self.bucket_name, Key=key)
        return response.get("Metadata", {})

    def generate_presigned_url(self, key: str, expiration: int = 3600, client_method: str = "get_object") -> str:
        logger.info("Generating presigned URL for key: %s", key)
        url: str = self._client.generate_presigned_url(
            ClientMethod=client_method,
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expiration,
        )
        return url

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError:
            return False
        return True

    def copy_object(self, source_key: str, destination_key: str) -> None:
        copy_source = {"Bucket": self.bucket_name, "Key": source_key}
        logger.info("Copying s3://%s/%s to s3://%s/%s", self.bucket_name, source_key, self.bucket_name, destination_key)
        self._client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=destination_key)

    def delete_object(self, key: str) -> None:
        logger.info("Deleting s3://%s/%s", self.bucket_name, key)
        self._client.delete_object(Bucket=self.bucket_name, Key=key)
