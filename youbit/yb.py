from __future__ import annotations
from typing import Optional, Any, Union, Tuple
from pathlib import Path
import atexit
import signal
import shutil
import tempfile
import os
import time
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
    def __init__(self, input: Union[str, Path]) -> None:
        self.input = Path(input)
        if not self.input.exists():
            raise ValueError(
                f"Invalid input argument '{input}'. Must be a valid file location."
            )
        if not self.input.is_file():
            raise ValueError("You must provide a file.")
        self.metadata: dict[str, Any] = {
            "original_MD5": youbit.util.get_md5(self.input),
            "file_extension": self.input.suffix,
        }
        TempdirMixin.__init__(self)

    def encode(
        self,
        path: Optional[Union[str, Path]] = None,
        ecc: Optional[int] = 32,
        res: Union[Tuple[int, int], str] = (1920, 1080),
        bpp: int = 1,
        crf: int = 18,
        zero_frame: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Encodes a file into a YouBit video.

        :param path: Use this parameter if you want to upload the
            video yourself. YouBit will create a directory at this path
            and save in it the encoded video as well as the required metadata.
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
        self.metadata["bpp"] = bpp
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
                    f"Invalid resolution argument '{res}'. Must be a tuple or one of 'hd', '2k', '4k' or '8k'."
                )
        self.metadata["zero_frame"] = zero_frame
        self.metadata["ecc_symbols"] = ecc
        if path:
            path = Path(path)
            if path.exists() and overwrite:
                shutil.rmtree(path)
            os.mkdir(path)
            readme_file = Path(os.path.dirname(__file__)) / "data" / "README_upload.txt"
            shutil.copy(readme_file, (path / "README.txt"))
            metadata_path = path / "metadata.txt"
            with open(metadata_path, "w") as f:
                f.write(youbit.util.dict_to_b64(self.metadata))
            if path.suffix not in (".mkv", ".mp4"):
                self.output = path / (path.name + ".mp4")
            else:
                self.output = path / path.name
        else:
            self.output = self.tempdir / "encoded.mp4"

        video_encoder = youbit.video.VideoEncoder(  # This goes first so that errors because of bad arguments can be raised before the actual encoding process, which can take a while.
            output=self.output,
            res=self.metadata["resolution"],
            crf=crf,
            zero_frame=zero_frame,
            overwrite=overwrite if path else True,
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

        if os.path.getsize(self.output) > 137000000000:
            raise RuntimeError("File is too large. The encoded video exceeds 128GB.")

    def upload(
        self, browser: str, title: str = str(time.time()), headless: bool = True
    ) -> str:
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
        :param title: The title for the video
        :type title: str
        :param headless: If set to False, Selenium will *not* run in headless
            mode and a browser window will appear on which you can inspect
            the automation. Defaults to True
        :type headless: bool, optional
        :return: Returns the URL of the uploaded video
        :rtype: str
        """
        uploader = youbit.upload.Uploader(browser=browser, headless=headless)
        description = youbit.util.dict_to_b64(self.metadata)
        video = self.tempdir / "encoded.mp4"
        url = uploader.upload(filepath=video, title=title, desc=description)
        self.close()
        return url


class Decoder(TempdirMixin):
    def __init__(self, input: Union[str, Path]):
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

    def download(
        self, path: Union[str, Path] = None
    ) -> None:  # TODO add an option to download video to local?
        if self.input_type != "url":
            raise ValueError(
                "You must initialize this object with a URL if you want to download anything."
            )
        if path:
            path = self.downloader.download(self.tempdir, Path(path))
        else:
            path = self.downloader.download(self.tempdir, self.tempdir)
            self.downloaded = path

    def decode(
        self,
        output: Union[str, Path],
        ecc: Optional[int] = None,
        bpp: Optional[int] = None,
        zero_frame: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Path:
        """Decodes a video back into original file.

        :param output: Path to save file to.
        :type output: str or Path
        :param ecc: Only required when video was downloaded manually.
            The amount of ECC symbols that were used during the encoding process.
            0 if no error correction was used. Defaults to None
        :type ecc: Optional[int], optional
        :param bpp: _description_, defaults to None
        :type bpp: Optional[int], optional
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
                raise ValueError(
                    "Download the video first."
                )  ## todo should not be valueerrror
            file = self.downloaded
            ecc = self.metadata["ecc_symbols"]
            bpp = self.metadata["bpp"]
            zero_frame = self.metadata["zero_frame"]
        elif self.input_type == "path":
            file = self.input  # type: ignore
            if bpp is None:
                raise ValueError("Missing argument: bpp")
            if ecc is None:
                raise ValueError("Missing argument: ecc")
            if zero_frame is None:
                raise ValueError("Missing argument: zero_frame")

        output = Path(output)
        if output.suffix != self.metadata["file_extension"]:
            output = Path(str(output) + self.metadata["file_extension"])
        if output.exists() and not overwrite:
            raise FileExistsError(f"File {output} already exists.")

        zipped_path = self.tempdir / "bin.gz"
        chunk_size = 255 * 1000000
        with youbit.video.VideoDecoder(vid=file):
            with open(zipped_path, "wb") as f:
                while True:
                    arr = youbit.video.VideoDecoder.get_array(chunk_size)
                    if not arr.size:
                        break
                    arr = youbit.decode.read_pixels(arr, bpp)
                    if ecc:
                        arr = youbit_ecc.ecc_decode(arr.tobytes(), ecc)
                    f.write(arr)

        with open(zipped_path, "rb") as f_in, gzip.open(output, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        self.new_md5 = youbit.util.get_md5(output)
        self.close()


        # frames = []
        # for frame in youbit.video.VideoDecoder(vid=file):
        #     frame = youbit.decode.read_pixels(frame, bpp)
        #     frames.append(frame)
        # output_arr = np.concatenate(frames, dtype=np.uint8)
        # if ecc > 0:
        #     output_bytes = youbit_ecc.ecc_decode(output_arr.tobytes(), ecc)
        #     with open(str(output), "wb") as f:
        #         f.write(output_bytes)
        # else:
        #     output_arr.tofile(str(output))
        # self.new_md5 = youbit.util.get_md5(output)
        # self.close()

    def verify_checksum(self) -> bool:
        """Compares the MD5 checksum of the original file to
        the MD5 of the newly decoded file.

        :return: Are the checksums equal?
        :rtype: bool
        """
        equal: bool = self.metadata["original_MD5"] == self.new_md5
        return equal
