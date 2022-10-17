from pathlib import Path
import shutil
import gzip

from youbit.tempdir import TempDir
from youbit.metadata import Metadata
from youbit.ecc.ecc import remove_ecc
from youbit.detransform import pixels_to_bytes
from youbit.download import Downloader
from youbit.video import VideoDecoder


def download_and_decode(url: str, output_dir: Path) -> None:
    tempdir = TempDir()
    downloader = Downloader(url)

    download_path = tempdir / "downloaded"
    downloader.download(download_path)

    decode_local(download_path, output_dir, downloader.youbit_metadata)
    tempdir.close()


def decode_local(input_file: Path, output_dir: Path, metadata: Metadata) -> Path:
    tempdir = TempDir()
    still_zipped_path = tempdir / "bin.gz"
    with VideoDecoder(input_file, metadata.settings) as decoder:
        with open(still_zipped_path, "wb") as file:
            chunk_size = 255000000  # Must be factor of 255 and 8.
            while True:
                pixeldata_arr = decoder.extract_pixeldata(chunk_size)
                if not pixeldata_arr.size:
                    break
                bytes_arr = pixels_to_bytes(pixeldata_arr, bpp)
                if metadata.settings.ecc_symbols:
                    bytes_arr = remove_ecc(
                        pixeldata_arr.tobytes(), 
                        metadata.settings.ecc_symbols
                    )
                file.write(bytes_arr)
    
    output_path = _create_valid_path(output_dir, metadata)
    _unzip_file(still_zipped_path, output_path)
    return output_path

def _unzip_file(input_file: Path, output_path: Path) -> None:
    with gzip.open(input_file, "rb") as f_in, open(output_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

def _create_valid_path(directory: Path, metadata: Metadata) -> Path:
    """Given a directory, returns a usable filepath within it."""
    original_filename = Path(metadata.filename)
    output = directory / original_filename
    i = 0
    while output.exists():
        i += 1
        output = Path(
            output.parent / (original_filename.stem + f"({i})" + original_filename.suffix)
        )
    return output
