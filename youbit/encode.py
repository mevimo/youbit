"""
The main API of YouBit.
"""
from __future__ import annotations 
from typing import Union
import gzip
import shutil
import os
from pathlib import Path

from youbit import util
from youbit.ecc.ecc import apply_ecc
from youbit.metadata import Metadata
from youbit.settings import Settings
from youbit.tempdir import TempDir
from youbit.transform import bytes_to_pixels
from youbit.upload import Uploader
from youbit.video import VideoEncoder


class Encoder:
    def __init__(self, input_file: Union[Path, str], settings: Settings = Settings()) -> None:
        input_file = Path(input_file)
        if not input_file.exists() or not input_file.is_file():
            raise ValueError(
                f"Invalid input argument '{input_file}'. Must be a valid file location."
            )
        
        self._input_file = input_file
        self._settings = settings
        self._metadata = Metadata(
            filename = str(self._input_file.name),
            md5_hash = util.get_md5(self._input_file),
            settings = self._settings
        )

    def encode_and_upload(self) -> str:
        with TempDir() as tempdir:
            video_temp_path = tempdir.path / "video.mp4"
            self._encode(video_temp_path)
            url = self._upload(video_temp_path)
        return url

    def encode_local(self, output_dir: Union[Path, str]) -> Path:
        output_dir = Path(output_dir)
        if not output_dir.exists() or not output_dir.is_dir():
            raise ValueError(f"'{output_dir}' is not a valid directory.")
    
        with TempDir() as tempdir:
            self._encode(tempdir.path / "video.mp4")
            output_path = output_dir / ("YOUBIT-" + self._metadata.filename)
            self._archive_dir_with_readme(tempdir.path, output_path)
            return output_path

    def _encode(self, output: Path) -> None:
        tempdir = TempDir()
        zipped_path = tempdir.path / 'zipped.bin'
        self._zip_file(zipped_path)

        video_encoder = VideoEncoder(output, self._settings)
        for chunk in self._read_chunks(zipped_path):
            if self._settings.ecc_symbols:
                chunk = apply_ecc(chunk, self._settings.ecc_symbols)
            pixels = bytes_to_pixels(chunk, self._settings.bits_per_pixel)
            video_encoder.feed(pixels)

        video_encoder.close()
        tempdir.close()

    def _zip_file(self, output_path: Path) -> None:
        with open(self._input_file, "rb") as f_in, gzip.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    def _archive_dir_with_readme(self, input_directory: Path, output: Path) -> Path:
        """Adds readme to given directory and archives its contens.
        """
        self._add_readme_to(input_directory)
        output_path = Path(shutil.make_archive(output, "zip", input_directory))
        return output_path

    def _add_readme_to(self, directory: Path) -> None:
        """Adds a readme file to the given directory with information
        about manual upload."""
        from_path = Path(os.path.dirname(__file__)) / "data" / "README_upload.txt"
        to_path = directory / "README.txt"
        shutil.copy(from_path, to_path)
        with open(to_path, "at") as readme:
            readme.write(self._metadata.export_as_base64())

    def _read_chunks(self, file: Path) -> bytes:
        """Reads the input file in PROPERLY SIZED chunks, returning it in bytes.
        This bytes object thus has a length that is a factor of (255 - ecc_symbols)!"""
        chunk_size = (255 - self._settings.ecc_symbols) * 100_000  # See apply_ecc()
        with open(file, "rb") as f:
            while True:
                binary_data = f.read(chunk_size)
                if not binary_data:
                    break
                yield binary_data

    def _upload(self, input_file: Path) -> str:
        uploader = Uploader(browser=self._settings.browser)
        url = uploader.upload(
            input_file = input_file,
            title = self._metadata.filename,
            description = self._metadata.export_as_base64()
        )
        return url
