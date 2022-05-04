import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(autouse=True)
def set_working_dir(request, monkeypatch):
    """Changes working directory to the directory of the test."""
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture
def tempdir():
    tempdir = Path(tempfile.mkdtemp(prefix='youbit-test-'))
    yield tempdir
    shutil.rmtree(tempdir)

