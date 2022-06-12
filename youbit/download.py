import os
from contextlib import redirect_stderr
from typing import Union
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from youbit import util


class InvalidYTDescription(Exception):
    """This exception is raised when YouBit metadata could not be extracted from YouTube comments."""
    def __init__(self, *args, msg='Could not extract YouBit metadata from YouTube video description.', **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(msg, *args, **kwargs)


class StillProcessingError(Exception):
    """This exception is raised when the expected resolution was not available for download.
    This is most likely because the video is still being processed by YouTUbe and not all streams
    are available yet."""
    def __init__(self, *args, msg='Correct resolution not found. Is the video still processing?', **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(msg, *args, **kwargs)


class Downloader:
    """Can downloads YouTube video's, automatically grabs the optimal format for YouBit.
    Also exposes the `get_metadata` property which returns the YouBit-specific metadata,
    extracted from the video description.
    """

    def __init__(self, url: str) -> None:
        """Checks the passed URL and gets metadata.
        Can take a moment."""
        self.url = url
        self.opts = {
            "logtostderr": True,
            'restrictfilenames': True,
            'windowsfilenames': True
        }
        with open(os.devnull, "wb") as devnull, redirect_stderr(devnull), YoutubeDL(self.opts) as ydl:  # yt-dlp will print 1ll raised exceptions to stderr, effectively writing dublicate information to terminal. There are no flags that alter this behavior.
            try:
                self._stream_info = ydl.extract_info(url, download=False)
            except DownloadError as e:
                raise DownloadError(f"Passed URL is invalid: {e}") from e
        try:
            self._yb_metadata = util.b64_to_dict(self._stream_info["description"])
        except Exception as e:
            raise InvalidYTDescription from e
        self.opts["format"] = self._format_selector

    def _format_selector(self, ctx: dict) -> dict:
        """Custom format selector for yt_dlp.
        Selects only formats witht the correct resolution, returning
        the one with the highest vide bitrate (vbr).

        :param ctx: The dictionary given by yt_dlp.
        :type ctx: dict
        :return: The selected format(s), for yt_dlp.
        :rtype: Iterator[dict]
        """
        formats = ctx.get("formats")
        desired_resolution = self._yb_metadata['resolution']
        formats = [
            f for f in formats if f["resolution"] == desired_resolution
        ]
        if len(formats) == 0:
            raise StillProcessingError
        formats.sort(reverse=True, key=lambda f: f["vbr"])
        best = formats[0]
        yield best

    def download(self, temp: Union[str, Path], output: Union[str, Path]) -> Path:
        """Downloads the video in question.

        :param temp: The path where the file are saved during download.
        :type temp: Union[str, Path]
        :param output: The path where the file will be moved to once downloading is finished.
        :type output: Union[str, Path]
        """
        self.opts['paths'] = {
            'temp': str(temp),
            'home': str(output)
        }
        with open(os.devnull, "wb") as devnull, redirect_stderr(devnull), YoutubeDL(self.opts) as ydl:
            ydl.download([self.url])
        file = [f for f in Path(output).iterdir() if f.is_file() and f.suffix in ('.mp4', '.mkv')][0]  # Assumes there to be no other .mp4 or .mkv files in the given output directory
        return file

    def get_metadata(self) -> dict:
        """Returns the YouBit metadata extract from the video description."""
        return self._yb_metadata.copy()
