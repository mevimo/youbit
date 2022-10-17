"""
YouBit: host any type of file on YouTube.
"""
from importlib.metadata import version
__title__ = "youbit"
__version__ = version("youbit")
__author__ = "Florian Laporte <florianl@florianl.dev>"
__license__ = "MIT License"

from .encode import Encoder
# from .decode import 
from .settings import Settings
from .metadata import Metadata
from . import transform
from . import detransform
from . import util
from . import video
from . import upload
from . import download
from .ecc import ecc


# __all__ = [
#     "Encoder",
#     "Decoder",
#     "encode",
#     "decode",
#     "download",
#     "upload",
#     "video",
#     "util",
#     "ecc"
# ]
