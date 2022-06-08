"""
YouBit: using YouTube as a very slow but free file hosting service.
"""
__title__= "youbit"
__version__ = "0.1.0"
__author__ = "Florian Laporte"
__license__ = "MIT License"

from youbit.__main__ import Encoder, Decoder
import youbit.encode as _encode
import youbit.decode as _decode
import youbit.util as _util
import youbit.video as _video
__all__ = ['Encoder', 'Decoder', '_encode', '_decode', '_util', '_video']




# import sys
# assert sys.version_info >= (2, 5)
##NOTE enforce minimum python version
