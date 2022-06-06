import re
from pathlib import Path
import hashlib
import os


def is_url(txt: str) -> bool:
    regex = "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    if re.search(regex, txt):
        return True
    else:
        return False


def get_md5(file: Path) -> str:
    with open(str(file), 'rb') as f:
        filesize = os.fstat(f.fileno()).st_size
        if filesize > 8589934592:
            raise ValueError('Files over 8GiB are currently not supported.')
        md5 = hashlib.md5()
        while True:
            data = f.read(65560)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()