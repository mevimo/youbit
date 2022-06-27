"""
This file (test_youbit.py.py) contains unit tests for the youbit.py file.
"""
from pathlib import Path
import os
import time

from yt_dlp.utils import DownloadError

from tests.conftest import uploads
from youbit import Encoder, Decoder
from youbit.download import StillProcessingError


@uploads
def test_youbit_round_trip(cmd_browser, tempdir):
    test_file = Path(os.getcwd()) / "testdata" / "files" / "test_file.jpg"
    with Encoder(test_file) as encoder:
        encoder.encode()
        url = encoder.upload(cmd_browser, title="unittest: test_youbit_round_trip")
    time.sleep(
        10
    )  # YouTube needs time to process the video before we can download the correct resolution
    timeout = 0
    while timeout < 60:
        try:
            with Decoder(url) as decoder:
                if decoder.downloader.best_vbr > 6000:
                    break
        except (StillProcessingError, DownloadError):
            time.sleep(5)
            timeout += 5
            continue
    if timeout >= 60:
        assert False, "Timeout"
    with Decoder(url) as decoder:
        decoder.download()
        decoder.decode(tempdir)
