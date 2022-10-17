from pathlib import Path

from youbit.tempdir import TempDir
from youbit.metadata import Metadata
from youbit.ecc.ecc import remove_ecc
from youbit.detransform import pixels_to_bytes
from youbit.download import Downloader


def download_and_decode(url: str, output: Path) -> None:
    _download()
    # build metadata object to pass to decode_local()
    decode_local()


def decode_local(input_file: Path, output: Path, metadata: Metadata) -> None:
    ...


def _download(url: str, output: Path) -> None:
    downloader = Downloader(url)


def _unzip_file() -> None:
    ...
