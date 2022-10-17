from typing import Any
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
        try:
            rmtree(self.path)
        except FileNotFoundError:
            pass

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()
