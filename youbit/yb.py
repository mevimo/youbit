"""
The main API of YouBit, concerns itself with I/O, chunking and temporary files.
"""
from __future__ import annotations
from typing import Optional, Any, Union, Tuple, Callable
from pathlib import Path
import atexit
import signal
import shutil
import tempfile
import os
import gzip

import numpy as np

import youbit.encode
import youbit.decode
import youbit.util
import youbit.ecc.ecc as youbit_ecc
import youbit.video
import youbit.download
import youbit.upload


class TempdirMixin:
    """Provides a temporary directory to use, as well as managing the cleanup
    of said directory through various mechanisms.
    Provides objects with a `close()` method to clean up the directory, as
    well as providing a context manager to enforce the cleanup.
    """

    def __init__(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="youbit-"))
        atexit.register(self.close)
        signal.signal(signal.SIGTERM, self.close)
        signal.signal(signal.SIGINT, self.close)

    def close(self) -> None:
        """Cleanup of temporary file directory."""
        try:
            shutil.rmtree(self.tempdir)
        except FileNotFoundError:
            pass

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()

    def __del__(self) -> None:
        # NOTE: `__del__` is very disliked and for good reason, but this is
        # just complimentary functionality in case it might ever catch an
        # edge-case not caught by the other mechanisms.
        self.close()


class Encoder(TempdirMixin):
    """Encodes files into YouBit videos, and optionally uploads them to YouTube."""
    def __init__(self, input_file: Union[str, Path]) -> None:
        self.input = Path(input_file)
        if not self.input.exists():
            raise ValueError(
                f"Invalid input argument '{input_file}'. Must be a valid file location."
            )
        if not self.input.is_file():
            raise ValueError("You must provide a file.")
        self.metadata: dict[str, Any] = {
            "original_MD5": youbit.util.get_md5(self.input),
            "filename": str(self.input.name),
        }
        TempdirMixin.__init__(self)

    def encode(
        self,
        directory: Optional[Union[str, Path]] = None,
        ecc: Optional[int] = 32,
        res: Union[Tuple[int, int], str] = (1920, 1080),
        bpp: int = 1,
        crf: int = 18,
        zero_frame: bool = False,
        # overwrite: bool = False,
    ) -> Optional[Path]:
        """Encodes a file into a YouBit video.

        :param directory: Use this parameter if you want to upload the
            video yourself. YouBit will create a a new directory in this
            directory and save in it the encoded video as well as the
            metadata required for upload.
        :type path: str or pathlike object, optional
        :param overwrite: If parameter `path` is specified, this parameter can
            be used to allow overwriting files at target location, defaults to
            False.
        :type overwrite: bool, optional
        :param ecc: How many ecc symbols to use for the reed-solomon encoding.
            Set to 0 to skip ecc encoding.
        :type ecc: int, optional
        :param res: Target resolution (width, height) of video. Supported resolutions
            are: (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320).
            Can also be a string, 'hd', '2k', '4k' or '8k.
            Defaults to (1920, 1080)
        :type res: tuple, optional
        :param bpp: Target 'bpp' of 'bits per pixel'. How many bits of
            information should be saved per pixel of video. Defaults to 2
        :type bpp: int, optional
        :param framerate: The framerate to use for the video, defaults to 1
        :type framrate: int, optional
        :param crf: the crf value to pass to the h.264 encoder, defaults to 18
        :type crf: int, optional
        :raises ValueError: If pixelsum of given argument res (width * height)
            is not divisible by 8.
        :raises ValueError: If argument crf is not in the range 0-52 inclusive.
        :raises ValueError: If argument bpp is an unsupported value.
        :raises FileNotFoundError: If argument path is an invalid filepath.
        :raises FileExistsError: If argument path points to an already
            existing file.
        """
        if isinstance(res, tuple):
            if res not in ((1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320)):
                raise ValueError(
                    "Invalid resolution. Supported resolutions are: "
                    "(1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320)"
                )
            self.metadata["resolution"] = res
        else:
            if res.lower() == "hd":
                self.metadata["resolution"] = (1920, 1080)
            elif res.lower() == "2k":
                self.metadata["resolution"] = (2560, 1440)
            elif res.lower() == "4k":
                self.metadata["resolution"] = (3840, 2160)
            elif res.lower() == "8k":
                self.metadata["resolution"] = (7680, 4320)
            else:
                raise ValueError(
                    f"Invalid resolution argument '{res}'."
                    "Must be a tuple or one of 'hd', '2k', '4k' or '8k'."
                )
        self.metadata["bpp"] = bpp
        self.metadata["zero_frame"] = zero_frame
        self.metadata["ecc_symbols"] = ecc
        output = self.tempdir / "video.mp4"

        video_encoder = youbit.video.VideoEncoder(
            output=output,
            res=self.metadata["resolution"],
            crf=crf,
            zero_frame=zero_frame,
        )

        zipped_path = self.tempdir / "bin.gz"
        with open(self.input, "rb") as f_in, gzip.open(zipped_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        # Calculate approximate video length, check if too long
        filesize = os.path.getsize(zipped_path)
        with_ecc_overhead = filesize * (255 / (255 - ecc))
        pixel_count = (with_ecc_overhead * 8) / bpp
        frame_count = pixel_count / (
            self.metadata["resolution"][0] * self.metadata["resolution"][1]
        )
        if zero_frame:
            frame_count = frame_count * 2
        if (
            frame_count > 43000
        ):  # the max video duration on YouTube is 12 hours or 43200 seconds
            raise RuntimeError(
                "File is too large. The given file with the given settings would produce "
                f"a video that is {frame_count} seconds long. The maximum is 43,000."
            )

        chunk_size = (255 - ecc) * 100000
        # If chunk_size is not a factor of (255-ecc), ecc_encode() will have to
        # add trailing empty bytes. We only want that at the end of our file,
        # where trailing null bytes do not matter. If they are added in the middle
        # of our binary, the file would obviously become corrupt.
        with open(zipped_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                if ecc:
                    data = youbit_ecc.ecc_encode(data, ecc)
                data = np.frombuffer(data, dtype=np.uint8)
                data = youbit.encode.transform_array(data, bpp)
                video_encoder.feed(data)
        video_encoder.close()
        zipped_path.unlink()

        if os.path.getsize(output) > 137000000000:
            raise RuntimeError("File is too large. The encoded video exceeds 128GB.")

        if directory:
            readme_file = Path(os.path.dirname(__file__)) / "data" / "README_upload.txt"
            shutil.copy(readme_file, (self.tempdir / "README.txt"))
            metadata_path = self.tempdir / "metadata.txt"
            with open(metadata_path, "wt") as f:
                f.write(youbit.util.dict_to_b64(self.metadata))
            output = directory / ("YOUBIT-" + self.metadata["filename"])
            output = shutil.make_archive(output, "zip", self.tempdir)
            return output

    def upload(self, browser: str, title: str = None, headless: bool = True) -> str:
        """Uploads the encoded file to YouTube. This process is automated
        with a Selenium webdriver, because of the various limitations on
        the YouTube API. This means this method needs a 'donor' browser
        to extract cookies from that can authenticate the webdriver to the
        account that you wish to use for upload. This process happens
        automatically, you need only pass which browser you want to use
        for this process. The account that is currently logged in to YouTube
        on that browser is the acocunt that will be used for the upload.

        MAKE SURE you have gone to 'studio.youtube.com' at least once on
        the account before, so that there are no popups left, such as
        consent popups and the 'choose channel name' popup. YouBit will
        not choose your channel name for you.

        :param browser: Which browser to extract cookies from. Can be
            'chrome', 'firefox', 'edge', 'opera', 'brave' or 'chromium'.
        :type browser: str
        :param title: The title for the video. If None, filename will be used.
            Defaults to None
        :type title: str, optional
        :param headless: If set to False, Selenium will *not* run in headless
            mode and a browser window will appear on which you can inspect
            the automation. Defaults to True
        :type headless: bool, optional
        :return: Returns the URL of the uploaded video
        :rtype: str
        """
        uploader = youbit.upload.Uploader(browser=browser, headless=headless)
        description = youbit.util.dict_to_b64(self.metadata)
        if title is None:
            title = self.metadata["filename"]
        video = self.tempdir / "video.mp4"
        url = uploader.upload(filepath=video, title=title, desc=description)
        return url


class Decoder(TempdirMixin):
    """Decodes YouBit videos back into the original file.
    Can also download them first."""
    def __init__(self, input: Union[str, Path], callback: Callable = None):
        if isinstance(input, str) and youbit.util.is_url(input):
            self.input: Union[str, Path] = input
            self.input_type = "url"
            self.downloader = youbit.download.Downloader(self.input)
            self.metadata = self.downloader.get_metadata()
            self.downloaded: Optional[Path] = None
        elif Path(input).exists() and Path(input).is_file():
            self.input = Path(input)
            self.input_type = "path"
        else:
            raise ValueError(
                "A valid filepath or url must be passed, neither was found."
            )
        TempdirMixin.__init__(self)
        self.new_md5: Optional[str] = None
        self.callback = callback

    def download(self) -> None:
        """Download the YouTube video in question.

        :raises ValueError: If the object was initialized with a path and not
            a url.
        """
        if self.input_type != "url":
            raise ValueError(
                "You must initialize this object with a URL if you want to download anything."
            )
        path = self.downloader.download(self.tempdir, self.tempdir)
        self.downloaded = path

    def decode(
        self,
        directory: Union[str, Path] = Path(os.getcwd()),
        ecc: Optional[int] = None,
        bpp: Optional[int] = None,
        zero_frame: Optional[bool] = None,
    ) -> Path:
        """Decodes a video back into original file.

        :param output: Directory in which to save the file. Defaults to the current
            working directory.
        :type output: str or Path
        :param ecc: The amount of ECC symbols that were used during the encoding process.
            0 if no error correction was used. Only required when decoding a local file
            and not a URL. Defaults to None
        :type ecc: int, optional
        :param bpp: What 'bpp' or 'bits per pixel' value was used during encoding.
            Only required when decoding a local file and not a URL. Defaults to None
        :type bpp: int, optional
        :param zero_frame: Whether not 'zero frames' were used during encoding. Only
            required when decoding a local file and not a URL. Defaults to None
        :type zero_frame: bool, optional
        :param overwrite: _description_, defaults to False
        :type overwrite: bool, optional
        :raises ValueError: _description_
        :raises ValueError: _description_
        :raises ValueError: _description_
        :return: _description_
        :rtype: Path
        """
        if self.input_type == "url":
            if not self.downloaded:
                raise RuntimeError("Download the video first.")
            file = self.downloaded
            og_filename = Path(self.metadata["filename"])
            ecc = self.metadata["ecc_symbols"]
            bpp = self.metadata["bpp"]
            zero_frame = self.metadata["zero_frame"]
        elif self.input_type == "path":
            file = self.input  # type: ignore
            og_filename = self.input.name
            if bpp is None:
                raise ValueError("Missing argument: bpp.")
            if ecc is None:
                raise ValueError("Missing argument: ecc.")
            if zero_frame is None:
                raise ValueError("Missing argument: zero_frame.")

        # output = Path(output)
        # if output.suffix != self.metadata["file_extension"]:
        #     output = Path(str(output) + self.metadata["file_extension"])
        # if output.exists() and not overwrite:
        #     raise FileExistsError(f"File {output} already exists.")
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory {directory} does not exist.")
        if not directory.is_dir():
            raise ValueError(f"{directory} is not a directory.")
        output = directory / og_filename
        i = 0
        while output.exists():
            i += 1
            output = Path(
                output.parent / (og_filename.stem + f"({i})" + og_filename.suffix)
            )

        zipped_path = self.tempdir / "bin.gz"
        chunk_size = (
            255 * 1000000
        )  # needs to be a factor of 255 (for ecc_decode) and 8 (for read_pixels)
        with youbit.video.VideoDecoder(vid=file, zero_frame=zero_frame) as decoder:
            with open(zipped_path, "wb") as f:
                while True:
                    arr = decoder.get_array(chunk_size)
                    if not arr.size:
                        break
                    arr = youbit.decode.read_pixels(arr, bpp)
                    if ecc:
                        arr = youbit_ecc.ecc_decode(arr.tobytes(), ecc)
                    f.write(arr)

        with gzip.open(zipped_path, "rb") as f_in, open(output, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        self.new_md5 = youbit.util.get_md5(output)
        self.close()
        return output

    def verify_checksum(self) -> bool:
        """Compares the MD5 checksum of the original file to
        the MD5 of the newly decoded file.

        :return: Are the checksums equal?
        :rtype: bool
        """
        equal: bool = self.metadata["original_MD5"] == self.new_md5
        return equal
