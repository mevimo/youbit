"""
Utility functions for YouBit.
"""
import re
import hashlib
from pathlib import Path
from typing import Union, Any

import av
import numpy as np


def is_url(txt: str) -> bool:
    """Check if passed string is a URL or not."""
    regex = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    if re.search(regex, txt):
        return True
    return False


def get_md5(file: Path) -> str:
    """Returns the MD5 checksum of the passed file."""
    with open(str(file), "rb") as f:
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


def analyze_gop(file: Union[str, Path]) -> dict[str, Any]:
    with av.open(str(file)) as container:
        stream = container.streams.video[0]
        closed_gop = stream.codec_context.closed_gop
        gop_size = stream.codec_context.gop_size
        frames = container.decode(stream)
        gops = []
        gop = []
        for f in frames:
            if f.pict_type.value == 1 and gop:
                gops.append(gop)
                gop = []
            gop.append(f.pict_type.name)
        gops.append(gop)
        gop_lengths = [len(gop) for gop in gops]
        total_frames = sum(gop_lengths)
        return {
            "total_frames": total_frames,
            "closed_gop": closed_gop,
            "gop_size": gop_size,
            "gop_count": len(gops),
            "gop_lengths": gop_lengths,
            "gops": gops,
        }
