"""
This file (test_youbit.py) contains unit tests for the encode.py and decode.py files.
"""
from pathlib import Path
import os
import time

from yt_dlp.utils import DownloadError

from tests.conftest import uploads
from youbit import Encoder, download_and_decode
from youbit.settings import Settings, Browser
from youbit.download import Downloader
from youbit.util import get_md5




from youbit import TempDir

@uploads
def test_youbit_round_trip(browser: Browser, tempdir: Path):
    test_file = Path(os.path.dirname(__file__)) / "testdata" / "files" / "test_file.jpg"
    encoder = Encoder(test_file, Settings(browser=browser))
    url = encoder.encode_and_upload()
    time.sleep(
        10
    )  # YouTube needs time to process the video before we can download the correct resolution
    timeout = 0
    while timeout < 60:
        try:
            downloader = Downloader(url)
            if downloader.best_vbr > 6000:
                break
        except DownloadError:
            time.sleep(5)
            timeout += 5
            continue
    if timeout >= 60:
        assert False, "Timeout"

    output_path = download_and_decode(url, tempdir)
    original_md5 = get_md5(test_file)
    output_md5 = get_md5(output_path)
    assert original_md5 == output_md5
    

if __name__ == "__main__":
    tempdir = TempDir()
    test_youbit_round_trip(Browser.FIREFOX, tempdir.path)
    tempdir.close()