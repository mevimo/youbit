"""
This file (test_core.py) contains unit tests for the core functionality of YouBit; the encoding and decoding process.
"""
import pytest
from youbit import lowlevel_encode, lowlevel_decode
from pathlib import Path
import os
import shutil
import hashlib


def test_video(tempdir):
    """
    GIVEN a video
    WHEN we disassemble it into images, and assemble those images back into a video
    THEN verify if the input and output video are identical
    """
    input_video_path = Path(os.getcwd()) / 'testdata' / 'video' / 'test_video.mp4'
    shutil.copy(input_video_path, tempdir)
    lowlevel_decode.extract_frames(tempdir)
    tempdir_size = len([_ for _ in tempdir.iterdir()])
    assert tempdir_size > 1, 'images were not extracted from video'

    output_video_path = lowlevel_encode.make_video(tempdir)
    assert output_video_path
    input_hash = hashlib.md5(open(input_video_path, 'rb').read()).hexdigest()
    output_hash = hashlib.md5(open(output_video_path, 'rb').read()).hexdigest()
    assert input_hash == output_hash, 'checksums of input and output file do not match'


def test_encode_decode(tempdir):
    """
    GIVEN a file
    WHEN we encode that file into a video, and decode that video back into a file
    THEN verify if input and ouput files are equal
    """
    pass


def test_ecc(tempdir):
    """
    GIVEN a file
    WHEN we apply error correction to that file, and then remove the error correction
    THEN verify if output matches original
    """
    pass