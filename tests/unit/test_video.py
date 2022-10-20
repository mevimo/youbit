"""
This file (test_video.py) contains unit tests for the video.py file.
"""
from pathlib import Path
import os
import warnings

import numpy as np

from youbit.video import VideoEncoder, VideoDecoder
from youbit.settings import Settings
from youbit.types import ndarr_1d_uint8
from youbit import util


# C_TEST_VIDEO_ENCODE_MD5_SOLUTION = "0dd13976862d4c1a5a5109c2825b8463"
C_TEST_VIDEO_ENCODE_MD5_SOLUTION = "537c69a0463b226967cdd40e1c32e506"



def test_video_encoder(tempdir: Path, test_arr: ndarr_1d_uint8) -> None:
    desired_filename = "test_video_encoded.mp4"
    output_path = tempdir / desired_filename
    with VideoEncoder(output_path, Settings()) as encoder:
        encoder.feed(test_arr)
    
    assert (
        util.get_md5(output_path) == C_TEST_VIDEO_ENCODE_MD5_SOLUTION
    )  # Compare MD5 checksum to md5 checksum of pre-computed and verified file.


def test_video_decoder(tempdir: Path, test_arr: ndarr_1d_uint8) -> None:
    video_filepath = tempdir / "input.mp4"
    settings = Settings()
    with VideoEncoder(video_filepath, settings) as encoder:
        encoder.feed(test_arr)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with VideoDecoder(video_filepath, settings) as decoder:
            output = list(decoder)
    output = np.concatenate(output, dtype=np.uint8)

    assert len(output) == len(test_arr)