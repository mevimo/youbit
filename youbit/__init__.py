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
from .settings import Settings, Browser
from .metadata import Metadata
from . import transform
from . import detransform
from . import util
from . import video
from . import upload
from . import download
from .ecc import ecc


__all__ = [
    "Encoder",
    "download_and_decode",
    "decode_local",
    "Settings",
    "Metadata"
]
