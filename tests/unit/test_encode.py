"""
This file (test_encode.py) contains unit tests for the encode.py file.
"""
from pathlib import Path
import os
import requests

import numpy as np

from youbit import encode


def test_lastframe_padding():
    """WHEN we call add_lastframe_padding() with an array of different arguments.
    THEN verify that the returned array's length is divisible by the expected framesize.
    """
    arrs = [
        np.random.randint(0,256,1000, dtype=np.uint8),
        np.random.randint(0,256,10000000, dtype=np.uint8)
    ]
    resolutions = [(1920,1080), (2560,1440), (3840,2160)]
    bpps = [1,2,3]
    for arr in arrs:
        for res in resolutions:
            for bpp in bpps:
                pixel_count = res[0] * res[1]
                framesize = int(pixel_count / 8) * bpp
                output = encode.add_lastframe_padding(arr, res, bpp)
                assert (output.size % framesize) == 0


def test_transform_array(tempdir, test_arr):
    """WHEN we use the transform_array() function on valid array.
    THEN verify if the returned array is of correct size AND equal to a precalculated and validated array.
    Please note the transform_array() function has exact requirements for the input array's size than need to be followed.
    """
    solution_bpp1 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_transform_array_solution_bpp1.npy'
    solution_bpp1 = np.load(solution_bpp1)

    solution_bpp2 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_transform_array_solution_bpp2.npy'
    solution_bpp2 = np.load(solution_bpp2)

    solution_bpp3 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_transform_array_solution_bpp3.npy'
    solution_bpp3 = np.load(solution_bpp3)

    for bpp in (1,2,3):
        output = encode.transform_array(test_arr, bpp)
        desired_size = int(test_arr.size * 8 / bpp)
        assert output.size == desired_size
        if bpp == 1:
            np.testing.assert_array_equal(output, solution_bpp1)
        elif bpp == 2:
            np.testing.assert_array_equal(output, solution_bpp2)
        elif bpp == 3:
            np.testing.assert_array_equal(output, solution_bpp3)
        else:
            assert False, 'No valid bbp value was detected, thus this test cannot be validated. This is an issue inside this test function.'
