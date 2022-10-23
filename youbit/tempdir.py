from __future__ import annotations
from pathlib import Path
from atexit import register
from signal import signal, SIGTERM, SIGINT
from shutil import rmtree
import tempfile


class TempDir:
    def __init__(self) -> None:
        self.path: Path = Path(tempfile.mkdtemp(prefix="youbit-"))
        register(self.close)
        signal(SIGTERM, self.close)
        signal(SIGINT, self.close)

    def close(self) -> None:
        print("close")
        try:
            rmtree(self.path)
        except FileNotFoundError:
            pass

    def __enter__(self) -> TempDir:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()
