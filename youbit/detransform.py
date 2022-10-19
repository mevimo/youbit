import numpy as np
from numba import njit

from youbit.types import ndarr_1d_uint8
from youbit.settings import BitsPerPixel


def pixels_to_bytes(arr: ndarr_1d_uint8, bpp: BitsPerPixel) -> ndarr_1d_uint8:
    """Reverses the bytes_to_pixels() function.
    Reads pixel values and returns the original binary.
    Array length must be a factor of 8!
    """
    if arr.size % 8:
        raise ValueError(
            f"The length of the given array ({arr.size}) is not a factor of 8."
        )
    
    sub_functions = {
        BitsPerPixel.ONE: _detransform_bpp1,
        BitsPerPixel.TWO: _detransform_bpp2,
        BitsPerPixel.THREE: _detransform_bpp3,
    }

    output = sub_functions[bpp](arr)
    return output


def _detransform_bpp1(arr: ndarr_1d_uint8) -> ndarr_1d_uint8:
    output = np.zeros(arr.size, dtype=np.uint8)
    _detransform_bpp1_subfunc(arr, output)
    array_of_bytes = np.packbits(output)
    return array_of_bytes


def _detransform_bpp2(arr: ndarr_1d_uint8) -> ndarr_1d_uint8:
    output_size = out_size = int(arr.size / 4)
    output = np.zeros(output_size, dtype=np.uint8)
    _detransform_bpp2_subfunc(arr, output)
    return output


def _detransform_bpp3(arr: ndarr_1d_uint8) -> ndarr_1d_uint8:
    output_size = int(arr.size / 8) * 3
    output = np.zeros(output_size, dtype=np.uint8)
    _detransform_bpp3_subfunc(arr, output)
    return output


@njit("void(uint8[::1], uint8[::1])")
def _detransform_bpp1_subfunc(arr, out) -> None:
    """Returns BITS not BYTES, still needs to be packed into the latter."""
    for i in range(out.size):
        out[i] = arr[i] >> 7


@njit("void(uint8[::1], uint8[::1])")
def _detransform_bpp2_subfunc(arr, out) -> None:
    for i in range(out.size):
        j = i * 4
        out[i] = (
            (arr[j] & 192)
            | ((arr[j + 1] & 192) >> 2)
            | ((arr[j + 2] & 192) >> 4)
            | ((arr[j + 3] & 192) >> 6)
        )


@njit("void(uint8[::1], uint8[::1])")
def _detransform_bpp3_subfunc(arr, out) -> None:
    for i in range(out.size // 3):
        arr_i = i * 8
        out_x3 = (
            ((arr[arr_i] & 224) << 16)
            | ((arr[arr_i + 1] & 224) << 13)
            | ((arr[arr_i + 2] & 224) << 10)
            | ((arr[arr_i + 3] & 224) << 7)
            | ((arr[arr_i + 4] & 224) << 4)
            | ((arr[arr_i + 5] & 224) << 1)
            | ((arr[arr_i + 6] & 224) >> 2)
            | ((arr[arr_i + 7] & 224) >> 5)
        )
        out_i = i * 3
        out[out_i] = out_x3 >> 16
        out[out_i + 1] = out_x3 >> 8 & 255
        out[out_i + 2] = out_x3 & 255
