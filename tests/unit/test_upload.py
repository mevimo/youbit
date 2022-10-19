"""
This file (test_upload.py) contains unit tests for the upload.py file.
"""
from pathlib import Path
import os
import requests

from youbit.upload import Uploader
from youbit.settings import Browser
from tests.conftest import uploads


C_TEST_VIDEO_PATH = Path(os.getcwd()) / "testdata" / "files" / "test_video.mp4"


@uploads
def test_upload(cmd_browser: Browser) -> None:
    """WHEN we use a youbit.uploader.Uploader object to upload a video.
    THEN verify if returned URL is valid, and title and description were set
    appropriately.

    Will upload a test video to YouTube. Test will be skipped unless
    commandline argument '--browser' is used to specify the browser to extract
    cookies from.

    This test is dirty as it leaves an uploaded video to a YouTube account that
    it cannot delete itself. You must delete these yourself.
    """
    title = "unittest_title"
    desc = "unittest_desc"
    uploader = Uploader(cmd_browser)
    url = uploader.upload(C_TEST_VIDEO_PATH, title=title, description=desc)
    assert url
    request = requests.get(url)
    assert request.status_code == 200
    assert title in request.text
    assert desc in request.text
