"""
This file (test_download.py) contains unit tests for the download.py file.
"""
from pathlib import Path

from youbit import Downloader, Metadata
from youbit.settings import Settings

from tests.conftest import long


TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dnhlx48t-h4"


@long
def test_best_vbr() -> None:
    downloader = Downloader(TEST_VIDEO_URL)
    assert downloader.best_vbr > 0


@long
def test_youbit_metadata() -> None:
    downloader = Downloader(TEST_VIDEO_URL)
    assert isinstance(downloader.youbit_metadata, Metadata)


@long
def test_download(tempdir: Path) -> None:
    """WHEN we use a Downloader object to download a YouTube video.
    THEN check if download succeeds and extracted metadata is correct.
    """
    downloader = Downloader(TEST_VIDEO_URL)
    output_path = tempdir / "video.mp4"
    downloader.download(output_path)
    assert output_path.exists()
    metadata = downloader.youbit_metadata
    assert isinstance(metadata, Metadata)
    assert metadata.filename == "youbit-example.jpg"
    assert isinstance(metadata.settings, Settings)
    assert metadata.md5_hash == "27ca391a382cc0287abd317904057125"
