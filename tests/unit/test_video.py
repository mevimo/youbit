"""
This file (test_video.py) contains unit tests for the video.py file.
"""
from pathlib import Path
import os
import warnings

import numpy as np

from youbit.video import VideoEncoder, VideoDecoder
from youbit.encode import add_lastframe_padding
from youbit import util


C_TEST_VIDEO_ENCODE_MD5_SOLUTION = "0dd13976862d4c1a5a5109c2825b8463"


def test_video_encoder(tempdir, test_arr):
    desired_filename = 'test_video_encoded.mp4'
    output_path = tempdir / desired_filename
    with VideoEncoder(output_path, overwrite=True) as encoder:
        encoder.feed(test_arr)
    tempdir_files = [x for x in tempdir.iterdir() if x.is_file()]
    assert len(tempdir_files) == 1
    output = tempdir_files[0]
    assert output.name == desired_filename
    assert util.get_md5(output) == C_TEST_VIDEO_ENCODE_MD5_SOLUTION # Compare MD5 checksum to md5 checksum of pre-computed and verified file.


def test_video_decoder(tempdir, test_arr):
    input = tempdir / 'input.mp4'
    with VideoEncoder(input, overwrite=True) as encoder:
        encoder.feed(test_arr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        output = list(VideoDecoder(input))
    output = np.concatenate(output, dtype=np.uint8)

    solution = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_video_decode_solution.npy'
    solution = np.load(solution)
    np.testing.assert_array_equal(output, solution)
