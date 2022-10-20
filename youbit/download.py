"""
Downloads the proper files from YouTube.
"""
import os
from contextlib import redirect_stderr
from typing import Optional
from pathlib import Path

from yt_dlp import YoutubeDL

from youbit.metadata import Metadata


class Downloader:
    C_YTDL_BASE_OPTIONS = {
        "logtostderr": True,
        "restrictfilenames": True,
        "windowsfilenames": True,
    }

    def __init__(self, url: str) -> None:
        self.url = url
        self.video_metadata = self._get_video_metadata()
        self.youbit_metadata = Metadata.create_from_base64(self.video_metadata["description"])

    @property
    def best_vbr(self) -> float:
        """Highest video bitrate that youbit can use, in Kbps."""
        try:
            best_format = next(self._format_selector(self.video_metadata))
        except StopIteration:
            return 0
        return best_format.get("vbr")

    def download(self, output: Path) -> None:
        ytdl_options = self.C_YTDL_BASE_OPTIONS.copy()
        ytdl_options.update({
            "paths": {"home": str(output)},
            "format": self._format_selector,
            "outtmpl": str(output)
        })
        
        with open(os.devnull, "w") as devnull, redirect_stderr(devnull):
            with YoutubeDL(ytdl_options) as ydl:
                ydl.download([self.url])

    def _get_video_metadata(self) -> dict:
        with open(os.devnull, "wb") as devnull, redirect_stderr(devnull):
            with YoutubeDL(self.C_YTDL_BASE_OPTIONS.copy()) as ydl:
                video_metadata = ydl.extract_info(self.url, download=False)
        return video_metadata

    def _format_selector(self, ctx: dict) -> Optional[dict]:
        """Custom format selector for yt_dlp.
        Returns the format with the highest bitrate and correct resolution, or None.
        NEEDS to be a generator for yt_dlp...
        """
        resolution: tuple = self.youbit_metadata.settings.resolution.value
        resolution_str = f"{resolution[0]}x{resolution[1]}"
        usable_formats = [
            format for format in ctx.get("formats") if format["resolution"] == resolution_str
        ]

        if len(usable_formats) == 0:
            return
        usable_formats.sort(reverse=True, key=lambda f: f["vbr"])
        yield usable_formats[0]
