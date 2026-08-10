from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from moto import mock_aws

from src.s3_client import S3Client, S3Settings

if TYPE_CHECKING:
    from pathlib import Path


def test_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "S3_BUCKET_NAME",
        "AWS_ENDPOINT_URL",
        "AWS_DEFAULT_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ):
        monkeypatch.delenv(key, raising=False)

    settings = S3Settings.from_env()

    assert settings.bucket_name == "terraform-localstack-demo"
    assert settings.endpoint_url == "http://localhost:4566"
    assert settings.region_name == "eu-west-1"
    assert settings.access_key_id == "test"
    assert settings.secret_access_key == "test"


def test_from_env_reads_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("S3_BUCKET_NAME", "custom-bucket")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "http://example:4566")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "custom-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "custom-secret")

    settings = S3Settings.from_env()

    assert settings.bucket_name == "custom-bucket"
    assert settings.endpoint_url == "http://example:4566"
    assert settings.region_name == "us-east-1"
    assert settings.access_key_id == "custom-key"
    assert settings.secret_access_key == "custom-secret"


def test_bucket_exists_true(s3_client: S3Client) -> None:
    assert s3_client.bucket_exists() is True


def test_bucket_exists_false(s3_settings: S3Settings) -> None:
    with mock_aws():
        client = S3Client(s3_settings)
        assert client.bucket_exists() is False


def test_upload_and_list_objects(s3_client: S3Client, tmp_path: Path) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_text("hello", encoding="utf-8")

    s3_client.upload_file(local_file, "hello.txt")

    assert s3_client.list_objects() == ["hello.txt"]
    assert s3_client.object_exists("hello.txt") is True


def test_object_exists_false_for_missing_key(s3_client: S3Client) -> None:
    assert s3_client.object_exists("missing.txt") is False


def test_download_file(s3_client: S3Client, tmp_path: Path) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_text("hello world", encoding="utf-8")
    s3_client.upload_file(local_file, "hello.txt")

    download_target = tmp_path / "downloaded.txt"
    s3_client.download_file("hello.txt", download_target)

    assert download_target.read_text(encoding="utf-8") == "hello world"


def test_delete_object(s3_client: S3Client, tmp_path: Path) -> None:
    local_file = tmp_path / "hello.txt"
    local_file.write_text("hello", encoding="utf-8")
    s3_client.upload_file(local_file, "hello.txt")

    s3_client.delete_object("hello.txt")

    assert s3_client.list_objects() == []


def test_list_objects_with_prefix(s3_client: S3Client, tmp_path: Path) -> None:
    file_a = tmp_path / "a.txt"
    file_a.write_text("a", encoding="utf-8")
    file_b = tmp_path / "b.txt"
    file_b.write_text("b", encoding="utf-8")

    s3_client.upload_file(file_a, "prefix/a.txt")
    s3_client.upload_file(file_b, "other/b.txt")

    assert s3_client.list_objects(prefix="prefix/") == ["prefix/a.txt"]
