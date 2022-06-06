"""
This file (test_decode.py) contains unit tests for the decode.py file.
"""
from youbit import decode
from pathlib import Path
import os
import numpy as np


def test_read_pixels():
    """WHEN we use the read_pixels() function on a valid array.
    THEN verify if the returned array is of correct size AND equal to a precalculated and validated array.
    """
    arr = [i for i in range(256)] * 8100 # makes the length exactly 2073600, or the sum of pixels in a 1920x1080 frame. 
    arr = np.array(arr, dtype=np.uint8)

    solution_bpp1 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_read_pixels_solution_bpp1.npy'
    solution_bpp1 = np.load(str(solution_bpp1))

    solution_bpp2 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_read_pixels_solution_bpp2.npy'
    solution_bpp2 = np.load(str(solution_bpp2))

    solution_bpp3 = Path(os.getcwd()) / 'testdata' / 'solutions' / 'test_read_pixels_solution_bpp3.npy'
    solution_bpp3 = np.load(str(solution_bpp3))

    for bpp in (1,2,3):
        output = decode.read_pixels(arr, bpp)
        desired_size = int(arr.size / 8) * bpp
        assert output.size == desired_size
        if bpp == 1:
            np.testing.assert_array_equal(output, solution_bpp1)
        elif bpp == 2:
            np.testing.assert_array_equal(output, solution_bpp2)
        elif bpp == 3:
            np.testing.assert_array_equal(output, solution_bpp3)
        else:
            assert False, 'No valid bbp value was detected, thus this test cannot be validated. This is an issue inside this test function.'