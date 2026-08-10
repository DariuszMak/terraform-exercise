from __future__ import annotations

from typing import TYPE_CHECKING

from src import main
from src.s3_client import S3Client

if TYPE_CHECKING:
    import pytest


def test_run_uploads_file_when_bucket_exists(
    monkeypatch: pytest.MonkeyPatch,
    s3_client: S3Client,
    tmp_path: pytest.TempPathFactory,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "load_dev_env", dict)
    monkeypatch.setattr(main.S3Client, "from_env", classmethod(lambda cls: s3_client))

    main.run()

    assert s3_client.list_objects() == ["test.txt"]


def test_run_skips_upload_when_bucket_missing(
    monkeypatch: pytest.MonkeyPatch,
    s3_settings: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    from moto import mock_aws

    monkeypatch.setattr(main, "load_dev_env", dict)

    with mock_aws():
        client = S3Client(s3_settings)  # type: ignore[arg-type]
        monkeypatch.setattr(main.S3Client, "from_env", classmethod(lambda cls: client))

        with caplog.at_level("ERROR"):
            main.run()

        assert any("does not exist" in message for message in caplog.messages)
