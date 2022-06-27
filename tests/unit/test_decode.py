"""
This file (test_decode.py) contains unit tests for the decode.py file.
"""
from pathlib import Path
import os

import numpy as np

from youbit import decode


def test_read_pixels(test_arr):
    """WHEN we use the read_pixels() function on a valid array.
    THEN verify if the returned array is of correct size AND
    equal to a precalculated and validated array.
    """
    solution_bpp1 = (
        Path(os.getcwd())
        / "testdata"
        / "solutions"
        / "test_read_pixels_solution_bpp1.npy"
    )
    solution_bpp1 = np.load(solution_bpp1)

    solution_bpp2 = (
        Path(os.getcwd())
        / "testdata"
        / "solutions"
        / "test_read_pixels_solution_bpp2.npy"
    )
    solution_bpp2 = np.load(solution_bpp2)

    solution_bpp3 = (
        Path(os.getcwd())
        / "testdata"
        / "solutions"
        / "test_read_pixels_solution_bpp3.npy"
    )
    solution_bpp3 = np.load(solution_bpp3)

    for bpp in (1, 2, 3):
        output = decode.read_pixels(test_arr, bpp)
        desired_size = int(test_arr.size / 8) * bpp
        assert output.size == desired_size
        if bpp == 1:
            np.testing.assert_array_equal(output, solution_bpp1)
        elif bpp == 2:
            np.testing.assert_array_equal(output, solution_bpp2)
        elif bpp == 3:
            np.testing.assert_array_equal(output, solution_bpp3)
        else:
            assert False, (
                "No valid bbp value was detected, thus this test cannot be validated."
                "This is an issue inside this test function."
            )
