from pathlib import Path

from youbit.tempdir import TempDir
from youbit.metadata import Metadata
from youbit.ecc.ecc import remove_ecc
from youbit.detransform import pixels_to_bytes
from youbit.download import Downloader


def download_and_decode(url: str, output: Path) -> None:
    tempdir = TempDir()
    downloader = Downloader(url)

    download_path = tempdir / "downloaded"
    downloader.download(download_path)

    decode_local(download_path, output, downloader.youbit_metadata)
    tempdir.close()


def decode_local(input_file: Path, output_dir: Path, metadata: Metadata) -> None:
    ...

def _create_valid_path(directory: Path, metadata: Metadata) -> Path:
    """Given a directory, returns a usable filepath within it."""


    output = directory / metadata.filename
    i = 0
    while output.exists():
        i += 1
        output = Path(
            output.parent / (og_filename.stem + f"({i})" + og_filename.suffix)
        )


def _unzip_file() -> None:
    ...
