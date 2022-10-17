"""
The main API of YouBit.
"""
from __future__ import annotations

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
    C_CHUNK_SIZE_FACTOR = 100000

    def __init__(self, input_file: Path, settings: Settings = Settings()) -> None:
        if not input_file.exists() or not input_file.is_file():
            raise ValueError(
                f"Invalid input argument '{input_file}'. Must be a valid file location."
            )
        
        self.input_file = input_file
        self.settings = settings
        self.metadata = Metadata(
            filename = str(self.input_file.name),
            md5_hash = util.get_md5(self.input_file),
            settings = self.settings
        )

    def encode_and_upload(self) -> str:
        with TempDir() as tempdir:
            video_temp_path = tempdir / "video.mp4"
            self._encode(video_temp_path)
            url = self._upload(video_temp_path)
        return url

    def encode_local(self, output_directory: Path) -> Path:
        with TempDir() as tempdir:
            self._encode(tempdir / "video.mp4")
            output_path = output_directory / ("YOUBIT-" + self.metadata.filename)
            self._archive_dir_with_readme(tempdir, output_path)
            return output_path

    def _encode(self, output: Path) -> None:
        tempdir = TempDir()
        zipped_path = tempdir / 'zipped.bin'
        self._zip_file(zipped_path)

        video_encoder = VideoEncoder(
            output = output,
            res = self.settings.resolution.value,
            crf = self.settings.constant_rate_factor,
            zero_frame = self.settings.null_frames,
        )

        for chunk in self._read_chunks(zipped_path):
            if self.settings.ecc_symbols:
                chunk = apply_ecc(chunk, self.settings.ecc_symbols)
            pixels = bytes_to_pixels(chunk, self.settings.bits_per_pixel)
            video_encoder.feed(pixels)

        video_encoder.close()
        tempdir.close()

    def _zip_file(self, output_path: Path) -> None:
        with open(self.input_file, "rb") as f_in, gzip.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    def _archive_dir_with_readme(self, input_directory: TempDir, output: Path) -> Path:
        """Adds readme to given directory and archives it.
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
            readme.write(self.metadata.export_as_base64())

    def _read_chunks(self, file: Path) -> bytes:
        chunk_size = (255 - self.settings.ecc_symbols) * self.C_CHUNK_SIZE_FACTOR
        with open(file, "rb") as f:
            while True:
                binary_data = f.read(chunk_size)
                if not binary_data:
                    break
                yield binary_data

    def _upload(self, input_file: Path) -> str:
        uploader = Uploader(browser=self.settings.browser)
        url = uploader.upload(
            input_file = input_file,
            title = self.metadata.filename,
            description = self.metadata.export_as_base64()
        )
        return url
