"""
Manages everything around the downloading process.
"""
import os
from contextlib import redirect_stderr
from typing import Union, Any, Optional, Tuple
from pathlib import Path
import warnings

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from youbit import util


class InvalidYTDescription(Exception):
    """This exception is raised when YouBit metadata
    could not be extracted from YouTube comments.
    """
    def __init__(
        self,
        *args,
        msg="Could not extract YouBit metadata from YouTube video description.",
        **kwargs,
    ):  # pylint: disable=useless-super-delegation
        super().__init__(msg, *args, **kwargs)


class StillProcessingError(Exception):
    """This exception is raised when the expected resolution was not available for download.
    This is most likely because the video is still being processed by YouTUbe and not all streams
    are available yet."""

    def __init__(
        self,
        *args,
        msg="Correct resolution not found. Is the video still processing?",
        **kwargs,
    ):  # pylint: disable=useless-super-delegation
        super().__init__(msg, *args, **kwargs)


class Downloader:
    """Can downloads YouTube video's, automatically grabs the optimal format for YouBit.
    Also exposes the `get_metadata` property which returns the YouBit-specific metadata,
    extracted from the video description.
    self.formats... self.info....
    """

    def __init__(self, url: str) -> None:
        """Checks the passed URL and gets metadata."""
        self.url = url
        self.opts: dict[str, Any] = {
            "logtostderr": True,
            "restrictfilenames": True,
            "windowsfilenames": True,
        }
        self.refresh()
        try:
            self._yb_metadata = util.b64_to_dict(self.info["description"])
        except Exception as e:
            raise InvalidYTDescription from e

    def refresh(self) -> None:
        """Extract video information, refreshing all video metadata in the object."""
        with open(os.devnull, "wb") as devnull, redirect_stderr(
            devnull
        ):  # yt-dlp will manually write raised exceptions to stderr,
            # in addition to raising the exception.
            with YoutubeDL(self.opts) as ydl:
                self.info = ydl.extract_info(self.url, download=False)
        self.formats = self.info["formats"]

    @property
    def best_vbr(self) -> int:
        """Returns the video bitrate of the format with the highest one currently available.
        Use self.refresh() to refresh this information as this might change as long as
        YouTube is processing the video (which goes on for much, much longer than
        the 'processing' popup remains visible).
        """
        desired_resolution = "{}x{}".format(
            self._yb_metadata["resolution"][0], self._yb_metadata["resolution"][1]
        )
        formats = [f for f in self.formats if f["resolution"] == desired_resolution]
        formats.sort(reverse=True, key=lambda f: f.get("vbr"))
        if len(formats) == 0:
            return 0
        return formats[0]["vbr"]

    def get_best_format(self) -> Tuple[int, list]:
        """Returns the video bitrate of the (usable) format with the highest one,
        as well as a list of all currently available formats.
        Can be useful to check if a format with a sufficiently high video bitrate
        is available yet.
        Often times, a video will have finished processing in a certain resolution,
        but only in a format with significantly less video bitrate than might be
        available a little later.
        """
        self.__init__(self.url)
        desired_resolution = "{}x{}".format(
            self._yb_metadata["resolution"][0], self._yb_metadata["resolution"][1]
        )
        formats = [f for f in self.formats if f["resolution"] == desired_resolution]
        formats.sort(reverse=True, key=lambda f: f.get("vbr"))
        return (formats[0]["vbr"], self.formats)

    def _format_selector(self, ctx: dict[Any, Any]) -> dict[Any, Any]:
        """Custom format selector for yt_dlp.
        Selects only formats witht the correct resolution, returning
        the one with the highest vide bitrate (vbr).

        :param ctx: The dictionary given by yt_dlp.
        :type ctx: dict
        :return: The selected format(s), for yt_dlp.
        :rtype: Iterator[dict]
        """
        formats: Optional[dict[Any, Any]] = ctx.get("formats")
        if not formats:
            raise RuntimeError("No formats found for download.")
        desired_resolution = "{}x{}".format(
            self._yb_metadata["resolution"][0], self._yb_metadata["resolution"][1]
        )
        usable_formats = [f for f in formats if f["resolution"] == desired_resolution]
        if len(usable_formats) == 0:
            raise StillProcessingError
        usable_formats.sort(reverse=True, key=lambda f: f["vbr"])
        best = usable_formats[0]
        if best["vbr"] < 6000:
            warnings.warn(
                f"A very low video bitrate (vbr) of {best['vbr']} was detected. "
                "The video is most likely not done processing, which might take "
                "a very long time to finish. There is a high chance the decoding "
                "process will fail because of this."
            )
        yield best

    def download(
        self, output: Union[str, Path], temp: Optional[Union[str, Path]] = None
    ) -> Path:
        """Downloads the video in question.

        :param output: The path where the file will be moved to once downloading is finished.
        :type output: Union[str, Path]
        :param temp: The path where the file is saved during download.
        :type temp: Union[str, Path]
        :raises DownloadError: If the download fails.
        :return: The path to the downloaded file.
        """
        self.opts["paths"] = {"home": str(output)}
        if temp:
            self.opts["paths"]["temp"] = str(temp)

        self.opts["format"] = self._format_selector
        try:
            with open(os.devnull, "w") as devnull, redirect_stderr(devnull):
                with YoutubeDL(self.opts) as ydl:
                    ydl.download([self.url])
        except DownloadError as e:
            if "processing" in str(e).lower():
                raise StillProcessingError from e
            else:
                raise e
        del self.opts[
            "format"
        ]  # So we can still use the .best_vbr property, since ytdlp will also use the custom format selector
        vid = (
            f for f in Path(output).iterdir()
            if f.is_file() and f.suffix in (".mp4", ".mkv", ".webm")
        )  # This is not great, I know
        return next(vid, None)

    def get_metadata(self) -> dict[Any, Any]:
        """Returns the YouBit metadata extract from the video description."""
        return self._yb_metadata.copy()
