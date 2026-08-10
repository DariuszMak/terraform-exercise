from __future__ import annotations

from typing import TYPE_CHECKING

import boto3
import pytest
from moto import mock_aws

from src.s3_client import S3Client, S3Settings

if TYPE_CHECKING:
    from collections.abc import Iterator

TEST_BUCKET_NAME = "terraform-localstack-demo"
TEST_REGION_NAME = "eu-west-1"


@pytest.fixture()
def s3_settings() -> S3Settings:
    return S3Settings(
        bucket_name=TEST_BUCKET_NAME,
        endpoint_url="",
        region_name=TEST_REGION_NAME,
        access_key_id="test",
        secret_access_key="test",
    )


@pytest.fixture()
def s3_client(s3_settings: S3Settings) -> Iterator[S3Client]:
    with mock_aws():
        boto3.client(
            "s3",
            region_name=s3_settings.region_name,
            aws_access_key_id=s3_settings.access_key_id,
            aws_secret_access_key=s3_settings.secret_access_key,
        ).create_bucket(
            Bucket=s3_settings.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": s3_settings.region_name},
        )
        yield S3Client(s3_settings)
