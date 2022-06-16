"""
This file (test_download.py) contains unit tests for the download.py file.
"""
from youbit.download import Downloader
from tests.conftest import long


C_TEST_VIDEO_URL = "https://www.youtube.com/watch?v=48jf81upU5M"
C_TEST_VIDEO_METADATA = {
    "original_MD5": "800235d5eb47e2684e333a33ca54a9aa",
    "ecc_symbols": 32,
    "bpp": 1,
    "resolution": "1920x1080",
}


@long
def test_download(tempdir):
    """WHEN we use a youbit.download.Downloader object to downlaod a YouTube video.
    THEN check if download succeeds and extracted metadata is correct. 
    """
    downloader = Downloader(C_TEST_VIDEO_URL)
    video_path = downloader.download(tempdir, tempdir)
    assert video_path.exists()
    metadata = downloader.get_metadata()
    assert metadata == C_TEST_VIDEO_METADATA
