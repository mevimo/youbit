import re
import hashlib
import os
import pickle
import base64
from pathlib import Path
from typing import Union, Any

import numpy as np

# from youbit.types import ndarr_1d_uint8


def dict_to_b64(obj: dict[Any, Any]) -> str:
    """Pickles a dictionary, encodes the output in a base64 string and returns the result."""
    return base64.b64encode(pickle.dumps(obj)).decode("utf8")


def b64_to_dict(b64: str) -> dict[Any, Any]:
    """Decodes a base64 string, and unpickles it back to the original dictionary."""
    return pickle.loads(base64.b64decode(bytes(b64, encoding="utf8")))


# def load_ndarray(file: Path) -> ndarr_1d_uint8:
#     """Reads a file and loads it into a numpy uin8 array."""
#     return np.fromfile(file, dtype=np.uint8)


# #! these 2 are supposed to have some chunking functionality or smthn idk


# def load_bytes(file: Union[Path, str]) -> bytes:
#     """Reads a file and loads it into a bytes object."""
#     with open(file, "rb") as f:
#         return f.read()


def is_url(txt: str) -> bool:
    """Check if passed string is a URL or not."""
    regex = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    if re.search(regex, txt):
        return True
    return False


# def bytes_to_ndarray(data: bytes) -> ndarr_1d_uint8:
#     return np.frombuffer(data, dtype=np.uint8)


def get_md5(file: Union[str, Path]) -> str:
    """Returns the MD5 checksum of the passed file."""
    with open(str(file), "rb") as f:
        filesize = os.fstat(f.fileno()).st_size
        if filesize > 8589934592:
            raise ValueError("Files over 8GiB are currently not supported.")
        md5 = hashlib.md5()
        while True:
            data = f.read(65560)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def compare_files(file1: Union[str, Path], file2: Union[str, Path]) -> dict[str, Any]:
    """Compares the binary information of 2 files, byte per byte.
    Returns a dictionary with information about the comparison.
    Makes no regard for memory usage: do not use with files that have
    a combined size larger than available system memory.

    Use this to compare the input and ouput of YouBit.
    """
    file1, file2 = Path(file1), Path(file2)
    arr1 = np.fromfile(file1, dtype=np.uint8)
    arr2 = np.fromfile(file2, dtype=np.uint8)
    size_difference = abs(arr1.size - arr2.size)
    zeros = np.zeros(size_difference, dtype=np.uint8)
    if arr1.size < arr2.size:
        arr1 = np.append(arr1, zeros)
    elif arr2.size < arr1.size:
        arr2 = np.append(arr2, zeros)
    assert arr1.size == arr2.size
    mask = np.equal(arr1, arr2)
    result = {
        "equal": np.array_equal(arr1, arr2),
        "total_byte_count": (total_byte_count := arr1.size),
        "correct_byte_count": (correct_byte_count := np.count_nonzero(mask)),
        "incorrect_byte_count": (
            incorrect_byte_count := arr1.size - correct_byte_count
        ),
        "error_rate": (incorrect_byte_count / total_byte_count) * 100,
        "mask": mask,
        "correct_indices": mask.nonzero()[0],
        "incorrect_indices": (~mask).nonzero()[0],
    }
    return result


def test_error_rate():
    pass
    ##  encode, upload, donwload, decode, and compare_files(). can only do once download and upload work
