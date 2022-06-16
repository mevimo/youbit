"""
This file (test_youbit.py.py) contains unit tests for the youbit.py file.
"""
from pathlib import Path
import os
import time

from youbit import Encoder, Decoder
<<<<<<< HEAD
from youbit.download import StillProcessingError
from tests.conftest import uploads
=======
from tests.conftest import uploads
from youbit.download import StillProcessingError
>>>>>>> main


@uploads
def test_youbit_round_trip(cmd_browser, tempdir):
    test_file = Path(os.getcwd()) / 'testdata' / 'files' / 'test_file.jpg'
    with Encoder(test_file) as encoder:
        encoder.encode()
        url = encoder.upload(cmd_browser, title='unittest: test_youbit_round_trip')
    time.sleep(10)  # YouTube needs time to process the video before we can download the correct resoltuion
    timeout = 0
    while timeout < 30:
        try:
            with Decoder(url) as decoder:
                decoder.download()
                decoder.decode(tempdir)
                assert decoder.verify_checksum()
                break
        except StillProcessingError:
            time.sleep(1)
            timeout += 1
            continue
