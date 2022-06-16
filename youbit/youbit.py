from __future__ import annotations
from typing import Optional, Any, Union
from pathlib import Path
import atexit
import signal
import shutil
import tempfile
import os
# import pyAesCrypt
import gzip
from zipfile import ZipFile

import numpy as np

from youbit import encode, decode, util
from youbit.ecc.ecc import ecc_encode, ecc_decode
from youbit.video import VideoDecoder, VideoEncoder
from youbit.download import Downloader
from youbit.upload import Uploader


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
        if os.path.getsize(self.input) > 1000000000:
            raise ValueError(
                "File too large. Only files up to 1GB are currently supported."
            )  #! raise or remove limit once chunking is in place
        self.metadata: dict[str, Any] = {
            "original_MD5": util.get_md5(self.input)
        }
        TempdirMixin.__init__(self)

    def encode(
        self,
        path: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
        ecc: Optional[int] = 32,
        res: tuple[int, int] = (1920, 1080),
        bpp: int = 1,
        crf: int = 18,
    ) -> None:
        #! if we want to zip and encrypt, we need to do it in-memory really...
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
        :param res: Target resolution (width, height) of video. Sum of pixels
            (width * height) must be divisible by 8. Defaults to (1920, 1080)
        :type res: tuple, optional
        :param bpp: Target 'bpp' of 'bits per pixel'. How many bits of
            information should be saved per pixel of video. Defaults to 2
        :type bpp: int, optional
        :param framerate: XXXXXXXXXXXXXXXXXXX, defaults to 1
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
        if path:
            path = Path(path)
            output = path / path.name
        else:
            output = self.tempdir / 'encoded.mp4'
        video_encoder = VideoEncoder(  # This goes first so that errors because of bad arguments can be raised before the actual encoding process, which can take a while.
            output=output,
            res=res,
            crf=crf,
            overwrite=overwrite if path else True,
        )

        if ecc:
            data = util.load_bytes(self.input)
            data = ecc_encode(data, ecc)
            arr = np.frombuffer(data, dtype=np.uint8)
            self.metadata["ecc_symbols"] = ecc
        else:
            arr = util.load_ndarray(self.input)
        arr = encode.add_lastframe_padding(arr, res, bpp)
        arr = encode.transform_array(arr, bpp)

        self.metadata["bpp"] = bpp
        self.metadata["resolution"] = f"{res[0]}x{res[1]}"
        try:
            if path:
                os.mkdir(path)
                readme_file = Path(os.path.dirname(__file__)) / 'data' / 'README_upload.txt'
                shutil.copy(readme_file, (path / 'README.txt'))
                with open((path / 'metadata.txt'), 'w') as f:
                    f.write(util.dict_to_b64(self.metadata))
            with video_encoder as video:
                video.feed(arr)
        except Exception as e:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass
            raise e
        if path:
            self.close()


    def upload(self, browser: str, title: str, headless=True) -> str:
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
            'chrome', 'firefox', 'edge', 'opera', 'brave' or 'chromium'. #! should be enum
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
        uploader = Uploader(browser=browser, headless=headless)
        description = util.dict_to_b64(self.metadata)
        video = self.tempdir / 'encoded.mp4'
        url = uploader.upload(filepath=video, title=title, desc=description)
        self.close()
        return url


class Decoder(TempdirMixin):
    def __init__(self, input: Union[str, Path]):
        if isinstance(input, str) and util.is_url(input):
            self.input: Union[str, Path] = input
            self.input_type = "url"
            self.downloader = Downloader(self.input)
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

    def download(self, path: Union[str, Path] = None) -> None:  #TODO add an option to download video to local?
        if self.input_type != 'url':
            raise ValueError('You must initialize this object with a URL if you want to download anything.')
        if path:
            path = self.downloader.download(self.tempdir, Path(path))
        else:
            path = self.downloader.download(self.tempdir, self.tempdir)
            self.downloaded = path

    def decode(self, output: Union[str, Path], ecc: Optional[int] = None, bpp: Optional[int] = None, overwrite: bool = False) -> Path:
        if self.input_type == "url":
            if not self.downloaded:
                raise ValueError('No downloaded video found.')  ## todo should not be valueerrror
            file = self.downloaded
            ecc = self.metadata['ecc_symbols']
            bpp = self.metadata['bpp']
        elif self.input_type == "path":
            file = self.input  # type: ignore
            if bpp is None:
                raise ValueError('Missing argument: bpp')
            if ecc is None:
                raise ValueError('Missing argument: ecc')
        frames = []
        for frame in VideoDecoder(vid=file):
            frame = decode.read_pixels(frame, bpp)
            frames.append(frame)
        output_arr = np.concatenate(frames, dtype=np.uint8)
        if ecc > 0:
            output_bytes = ecc_decode(output_arr.tobytes(), ecc)
            with open(str(output), 'wb') as f:
                f.write(output_bytes)
        else:
            output_arr.tofile(str(output))
        # decrypt and or unzip in-memory
        ##TODO: overwrite logic here maybe use normal writing bytes or smthn
        self.new_md5 = util.get_md5(output)
        self.close()

    def verify_checksum(self) -> bool:
        """Compares the MD5 checksum of the original file to
        the MD5 of the newly decoded file.

        :return: Are the checksums equal?
        :rtype: bool
        """
        equal: bool = self.metadata['original_MD5'] == self.new_md5
        return equal
