"""
This file (test_upload.py) contains unit tests for the upload.py file.
"""
from pathlib import Path
import os
import requests

from youbit.upload import Uploader
from tests.conftest import uploads


@uploads
def test_upload(cmd_browser):
    """WHEN we use a youbit.uploader.Uploader object to upload a video.
    THEN verify if returned URL is valid, and title and description were set
    appropriately.
    
    Will upload a test video to YouTube. Test will be skipped unless
    commandline argument '--browser' is used to specify the browser to extract
    cookies from. Read more about the upload process `here`.
    Browser can be any of ('chrome', 'firefox', 'brave', 'chromium', 'edge', 'opera').

    This test is dirty as it leaves an uploaded video to a YouTube account that
    it cannot delete itself. You must delete these yourself.
    """
    title = 'unittest_title'
    desc = 'unittest_desc'
    uploader = Uploader(cmd_browser)
    test_video = Path(os.getcwd()) / 'testdata' / 'files' / 'test_video.mp4'
    url = uploader.upload(test_video, title=title, desc=desc)
    assert url
    request = requests.get(url)
    assert request.status_code == 200
    assert title in request.text
    assert desc in request.text
