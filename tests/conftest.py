import pytest
from pathlib import Path
import tempfile
import shutil
import numpy as np
from pathlib import Path


@pytest.fixture(autouse=True)
def set_working_dir(request, monkeypatch):
    """Changes working directory to the directory of the test."""
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture
def tempdir() -> Path:
    tempdir = Path(tempfile.mkdtemp(prefix='youbit-test-'))
    yield tempdir
    shutil.rmtree(tempdir)


@pytest.fixture
def test_arr() -> np.ndarray[(1,), np.uint8]:
    arr = [i for i in range(256)] * 8100 # makes the length exactly 2073600, or the sum of pixels in a 1920x1080 frame. 
    arr = np.array(arr, dtype=np.uint8)
    return arr