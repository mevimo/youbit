"""
This file (test_transform.py) contains unit tests for the transform.py file.
"""
from pathlib import Path
import os

import numpy as np

from youbit import transform
from youbit.types import ndarr_1d_uint8
from youbit.settings import BitsPerPixel


def test_bytes_to_pixels(test_arr: ndarr_1d_uint8) -> None:
    """WHEN we use the transform_array() function on valid array.
    THEN verify if the returned array is of correct size
    AND equal to a precalculated and validated array.
    """
    solution_bpp1 = (
        Path(os.path.dirname(__file__))
        / "testdata"
        / "solutions"
        / "test_transform_array_solution_bpp1.npy"
    )
    solution_bpp1 = np.load(solution_bpp1)

    solution_bpp2 = (
        Path(os.path.dirname(__file__))
        / "testdata"
        / "solutions"
        / "test_transform_array_solution_bpp2.npy"
    )
    solution_bpp2 = np.load(solution_bpp2)

    solution_bpp3 = (
        Path(os.path.dirname(__file__))
        / "testdata"
        / "solutions"
        / "test_transform_array_solution_bpp3.npy"
    )
    solution_bpp3 = np.load(solution_bpp3)

    solutions = {
        BitsPerPixel.ONE: solution_bpp1,
        BitsPerPixel.TWO: solution_bpp2,
        BitsPerPixel.THREE: solution_bpp3
    }

    for bpp in BitsPerPixel:
        output = transform.bytes_to_pixels(test_arr, bpp)
        desired_size = int(test_arr.size * 8 / bpp.value)
        assert output.size == desired_size
        np.testing.assert_array_equal(output, solutions[bpp])
