"""
YouBit: host any type of file on YouTube.
"""
from importlib.metadata import version

__title__ = "youbit"
__version__ = version("youbit")
__author__ = "Florian Laporte <florianl@florianl.dev>"
__license__ = "MIT License"

from .encode import Encoder
from .decode import download_and_decode, decode_local
from .metadata import Metadata
from .upload import Uploader
from .download import Downloader
from . import settings
from . import transform
from . import detransform
from . import util
from . import video
from .tempdir import TempDir
from .ecc import ecc


__all__ = ["Encoder", "download_and_decode", "decode_local", "Settings", "Metadata"]
