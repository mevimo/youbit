from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError, DownloadError
import os
from contextlib import redirect_stderr


# C_OPTS = {
#     'logtostderr': True,
#     'format_sort': ['vext', 'vbr']
# }


def get_metadata(URL: str) -> dict:
    opts = {'logtostderr': True}
    devnull = open(os.devnull, 'w')
    with redirect_stderr(open(os.devnull, 'w')): # yt-dlp will print the error message to stderr in addition to raising an exception, effectively writing dublicate information to terminal. There are no flags that alter this behavior.
        with YoutubeDL(opts) as ydl:
            try:
                metadata = ydl.extract_info(URL, download=False)
            except DownloadError as e:
                raise ValueError(f'Passed url is invalid: {e}')
            # ydl.download([URL])
    return metadata



class Downloader:

    def __init__(self, url: str):
        self.opts = {'logtostderr': True}
        with open(os.devnull, 'w') as devnull, redirect_stderr(devnull), YoutubeDL(self.opts) as ydl: # yt-dlp will print the error message to stderr in addition to raising an exception, effectively writing dublicate information to terminal. There are no flags that alter this behavior.
            try:
                info = ydl.extract_info(url, download=False)
            except DownloadError as e:
                raise ValueError(f'Passed url is invalid: {e}')
            # self.yb_metadata = from comments
            # check if vid is actually youbit video

    def _format_selector(self, ctx):
        all_formats = ctx.get('formats')
        correct_resolution = [f for f in all_formats if f['resolution'] == '1920x1080'] #TODO needs to be replaced
