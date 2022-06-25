import numpy as np
from numba import njit

from youbit.types import ndarr_1d_uint8


@njit('void(uint8[::1], uint8[::1])')
def _numba_read_bpp1(arr, out) -> None:
    """ still needs to be packed"""
    for i in range(out.size):
        out[i] = arr[i] >> 7


@njit('void(uint8[::1], uint8[::1])')
def _numba_read_bpp2(arr, out) -> None:
    for i in range(out.size):
        j = i * 4
        out[i] = (arr[j] & 192) \
            | ((arr[j+1] & 192) >> 2) \
            | ((arr[j+2] & 192) >> 4) \
            | ((arr[j+3] & 192) >> 6)
    

@njit('void(uint8[::1], uint8[::1])')
def _numba_read_bpp3(arr, out) -> None:
    for i in range(out.size//3):
        arr_i = i * 8
        out_x3 = ((arr[arr_i] & 224) << 16) \
            | ((arr[arr_i+1] & 224) << 13) \
            | ((arr[arr_i+2] & 224) << 10) \
            | ((arr[arr_i+3] & 224) << 7) \
            | ((arr[arr_i+4] & 224) << 4) \
            | ((arr[arr_i+5] & 224) << 1) \
            | ((arr[arr_i+6] & 224) >> 2) \
            | ((arr[arr_i+7] & 224) >> 5)
        out_i = i * 3
        out[out_i] = out_x3 >> 16
        out[out_i+1] = out_x3 >> 8 & 255
        out[out_i+2] = out_x3 & 255


def read_pixels(arr: ndarr_1d_uint8, bpp: int) -> ndarr_1d_uint8:
    """Reads a uint8 numpy array where each element represents a
    pixel of a YouBit video. Returns the decoded array, where each
    element represents a byte.
    The reverse of youbit.encode.transform_array().
    Since the elements are joined back together into bytes,
    the input array needs to be a factor of 8.
    """
    if arr.size % (bpp * 8):
        raise ValueError(f'The length of the given array ({arr.size}) is not divisible by 8.')
    if bpp == 1:
        out = np.zeros(arr.size, dtype=np.uint8)
        _numba_read_bpp1(arr, out)
        out = np.packbits(out)
    elif bpp == 2:
        out_size = int(arr.size / 4)
        out = np.zeros(out_size, dtype=np.uint8)
        _numba_read_bpp2(arr, out)
    elif bpp == 3:
        out_size = int(arr.size / 8) * 3
        out = np.zeros(out_size, dtype=np.uint8)
        _numba_read_bpp3(arr, out)
    return out
