from __future__ import annotations

import logging
import os
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
            "config": Config(s3={"addressing_style": "path"}),
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

    def upload_file(self, local_path: Path, key: str) -> None:
        logger.info("Uploading %s to s3://%s/%s", local_path, self.bucket_name, key)
        self._client.upload_file(str(local_path), self.bucket_name, key)

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

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError:
            return False
        return True

    def delete_object(self, key: str) -> None:
        logger.info("Deleting s3://%s/%s", self.bucket_name, key)
        self._client.delete_object(Bucket=self.bucket_name, Key=key)
