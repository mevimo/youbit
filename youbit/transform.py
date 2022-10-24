"""
This file concerns itself with the transformation of binary data
in such a way that it can be used as pixel-values in a picture or video.
"""
import numpy as np
from numba import njit, prange
from typing import Union

from youbit.settings import BitsPerPixel
from youbit.types import ndarr_1d_uint8


def bytes_to_pixels(
    input_data: Union[ndarr_1d_uint8, bytes], bpp: BitsPerPixel
) -> ndarr_1d_uint8:
    """Transforms binary data into a uint8 numpy array representing 8 bit
    greyscale pixels for a YouBit video.
    BEWARE: when the input has a length that is not a factor of 8, this function
    might append nulls to make it so. You should only let this happen at the very
    end of a file's binary data, NOT in the middle of it.
    """
    if isinstance(input_data, bytes):
        input_data: ndarr_1d_uint8 = np.frombuffer(input_data, dtype=np.uint8)
    _add_trailing_bytes_if_necessary(input_data, bpp)

    SUB_FUNCTIONS = {
        BitsPerPixel.ONE: _transform_bpp1,
        BitsPerPixel.TWO: _transform_bpp2,
        BitsPerPixel.THREE: _transform_bpp3
    }

    input_data = np.unpackbits(input_data)
    output = np.zeros(int(input_data.size / bpp.value), dtype=np.uint8)
    SUB_FUNCTIONS[bpp](input_data, output)
    return output


def _add_trailing_bytes_if_necessary(
    ndarray: ndarr_1d_uint8, bpp: BitsPerPixel
) -> None:
    """With a bpp of 3, every byte cannot be transformed into a whole number of pixels.
    The smallest chunk is 3 bytes, or 24 bits, which results in 8 pixels."""
    if bpp is BitsPerPixel.THREE and (mod := ndarray.size % 3):
        addition = np.zeros((3 - mod), dtype=np.uint8)
        input_data = np.append(input_data, addition)


@njit("void(uint8[::1], uint8[::1])", parallel=True)
def _transform_bpp1(arr, out) -> None:
    MAPPING = np.array([0, 255], dtype=np.uint8)
    for i in prange(out.size):
        out[i] = MAPPING[arr[i]]


@njit("void(uint8[::1], uint8[::1])", parallel=True)
def _transform_bpp2(arr, out) -> None:
    MAPPING = np.array([0, 96, 160, 255], dtype=np.uint8)
    for i in prange(out.size):
        j = i * 2
        out[i] = MAPPING[(arr[j] << 1) | (arr[j + 1])]


@njit("void(uint8[::1], uint8[::1])", parallel=True)
def _transform_bpp3(arr, out) -> None:
    MAPPING = np.array([0, 48, 80, 112, 144, 176, 208, 255], dtype=np.uint8)
    for i in prange(out.size):
        j = i * 3
        out[i] = MAPPING[(arr[j] << 2) | (arr[j + 1] << 1) | (arr[j + 2])]
