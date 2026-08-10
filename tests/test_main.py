from __future__ import annotations

from typing import TYPE_CHECKING

from moto import mock_aws

from src import main
from src.s3_client import S3Client, S3Settings

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_run_uploads_file_when_bucket_exists(
    monkeypatch: pytest.MonkeyPatch,
    s3_client: S3Client,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "load_dev_env", dict)
    monkeypatch.setattr(main.S3Client, "from_env", classmethod(lambda cls: s3_client))

    main.run()

    assert s3_client.list_objects() == ["test.txt"]


def test_run_skips_upload_when_bucket_missing(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(main, "load_dev_env", dict)

    with mock_aws():
        settings = S3Settings(
            bucket_name="does-not-exist-bucket",
            endpoint_url="",
            region_name="eu-west-1",
            access_key_id="test",
            secret_access_key="test",
        )
        client = S3Client(settings)
        monkeypatch.setattr(main.S3Client, "from_env", classmethod(lambda cls: client))

        with caplog.at_level("ERROR"):
            main.run()

        assert any("does not exist" in message for message in caplog.messages)
