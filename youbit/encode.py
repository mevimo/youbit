"""
This file concerns itself with the transformation of binary data
in such a way that it can be used as pixel-values in a picture or video.
"""
import numpy as np
from numba import njit, prange

from youbit.types import ndarr_1d_uint8


@njit("void(uint8[::1], uint8[::1], uint8[::1])", parallel=True)
def _numba_transform_bpp1(arr, out, mapping) -> None:
    for i in prange(out.size):
        out[i] = mapping[arr[i]]


@njit("void(uint8[::1], uint8[::1], uint8[::1])", parallel=True)
def _numba_transform_bpp2(arr, out, mapping) -> None:
    for i in prange(out.size):
        j = i * 2
        out[i] = mapping[(arr[j] << 1) | (arr[j + 1])]


@njit("void(uint8[::1], uint8[::1], uint8[::1])", parallel=True)
def _numba_transform_bpp3(arr, out, mapping) -> None:
    for i in prange(out.size):
        j = i * 3
        out[i] = mapping[(arr[j] << 2) | (arr[j + 1] << 1) | (arr[j + 2])]


def transform_array(arr: ndarr_1d_uint8, bpp: int) -> ndarr_1d_uint8:
    """Transforms a uint8 numpy array (0, 255, 38, ..) into a uint8 numpy array
    representing 8 bit greyscale pixels in a YouBit video.
    The output depends on the 'bpp' (or 'bits per pixel') parameter.

    It does this by first unpacking the array into a binary representation of it
    (essentially converting from decimal to binary, 65 -> 01000001).
    It then groups consecutive binary digits into groups of {bpp}, before mapping
    these groups to an appropriate pixel value.

    IF bpp is 3 and the length of the given array is not a factor of 3, this function
    will append 1 or 2 null bytes to the input array!
    """
    if bpp == 3 and (mod := arr.size % 3):
        addition = np.zeros((3 - mod), dtype=np.uint8)
        arr = np.append(arr, addition)
    arr = np.unpackbits(arr)
    div = int(arr.size / bpp)
    out = np.zeros(div, dtype=np.uint8)
    if bpp == 1:
        mapping = np.array([0, 255], dtype=np.uint8)
        _numba_transform_bpp1(arr, out, mapping)
    elif bpp == 2:
        mapping = np.array([0, 96, 160, 255], dtype=np.uint8)
        _numba_transform_bpp2(arr, out, mapping)
    elif bpp == 3:
        mapping = np.array([0, 48, 80, 112, 144, 176, 208, 255], dtype=np.uint8)
        _numba_transform_bpp3(arr, out, mapping)
    else:
        raise ValueError(f"Unsupported bpp argument: {bpp} of type {type(bpp)}.")
    return out
