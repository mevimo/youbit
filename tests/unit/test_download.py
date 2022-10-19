"""
This file (test_download.py) contains unit tests for the download.py file.
"""
from youbit.download import Downloader
from tests.conftest import long

#! has to be redone by changing description of old video


C_TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dnhlx48t-h4"
C_TEST_VIDEO_METADATA = {
    "original_MD5": "27ca391a382cc0287abd317904057125",
    "filename": "youbit-example.jpg",
    "resolution": (1920, 1080),
    "bpp": 1,
    "zero_frame": False,
    "ecc_symbols": 32,
}


@long
def test_download(tempdir):
    """WHEN we use a Downloader object to download a YouTube video.
    THEN check if download succeeds and extracted metadata is correct.
    """
    downloader = Downloader(C_TEST_VIDEO_URL)
    video_path = downloader.download(tempdir, tempdir)
    assert video_path.exists()
    metadata = downloader.get_metadata()
    assert metadata == C_TEST_VIDEO_METADATA
