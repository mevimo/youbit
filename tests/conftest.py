from pathlib import Path
import shutil

import tempfile
import numpy as np
import pytest

from youbit.types import ndarr_1d_uint8


uploads = pytest.mark.skipif(
    "not config.getoption('--browser') or not config.getoption('--long')"
)
long = pytest.mark.skipif("not config.getoption('--long')")


@pytest.fixture(autouse=True)
def set_working_dir(request, monkeypatch):
    """Changes working directory to the directory of the test."""
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture
def tempdir() -> Path:
    tempdir = Path(tempfile.mkdtemp(prefix="youbit-test-"))
    yield tempdir
    shutil.rmtree(tempdir)


@pytest.fixture
def test_arr() -> ndarr_1d_uint8:
    arr = [
        i for i in range(256)
    ] * 8100  # makes the length exactly 2073600, or the sum of pixels in a 1920x1080 frame.
    arr = np.array(arr, dtype=np.uint8)
    return arr


def pytest_addoption(parser):
    parser.addoption(
        "--long",
        action="store_true",
        default=False,
        help="Also run tests that may be very slow due to networking.",
    )
    parser.addoption(
        "--browser",
        action="store",
        help="Enables upload tests. Specify which browser should be used to extract cookies from. These tests are dirty since they leave uploaded videos behind that they cannot clean up.",
        choices=("chrome", "firefox", "opera", "brave", "edge", "chromium"),
    )


@pytest.fixture
def cmd_browser(request):
    return request.config.getoption("--browser")
