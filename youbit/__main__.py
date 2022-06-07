from __future__ import annotations
from sys import path_hooks
from tkinter.tix import InputOnly
from typing import List, Dict, Optional, Any, Tuple, Callable, Union
from pathlib import PurePath, Path
from pytube import YouTube
import hashlib
import atexit
import signal
import shutil
import tempfile
import os
import pyAesCrypt
import json
import gzip
from zipfile import ZipFile
import re
import numpy as np

# from youbit.automate import Uploader
# from youbit.decode import remove_ecc, extract_frames, extract_binary
from youbit import encode, decode, util
from youbit._video_code import VideoDecoder, VideoEncoder


class TempDirMixin:
    """Provides a temporary directory to use, as well as managing the cleanup of said directory through various mechanisms.
    Provides classes implementing this mixin with a `close()` method to clean up the directory, as well as providing a context manager
    to enforce the cleanup."""
    def __init__(self):
        self.tempdir = tempfile.mkdtemp(prefix='youbit-')
        atexit.register(self.close)
        signal.signal(signal.SIGTERM, self.close)
        signal.signal(signal.SIGINT, self.close)

    def close(self) -> None:
        """Cleanup of temporary file directory."""
        try:
            shutil.rmtree(self.tempdir)
        except FileNotFoundError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        #NOTE: `__del__` is extremely unreliable as there if very little guarantee it will ever be called. This is just complimentary functionality in case it might ever catch an edge-case not caught by the other mechanisms.
        self.close()
    

class Encoder(TempDirMixin):

    def __init__(self, input: Union[str, Path]) -> None:
        input = Path(input)
        if not input.exists():
            raise ValueError(f"Invalid input argument '{input}'. Must be a valid file location.")
        if not input.is_file():
            raise ValueError('You must provide a file.')
        if os.path.getsize(input) > 1000000000:
            raise ValueError('File too large. Only files up to 1GB are currently supported.')
        self.input = Path(input)
        self.metadata = {
            'original_filename': self.input.name, # prob not necessary
            'original_MD5': util.get_md5(self.input),
        }
        TempDirMixin.__init__(self)

    def encode(self, path: Union[str, Path], res: tuple[int, int] = (1920, 1080), bpp: int = 2, framerate: int = 1, crf: int = 0, overwrite: bool = False) -> None:
        #! if we want to zip and encrypt, we need to do it in-memory really...
        """Encodes a file into a YouBit video.
        
        :param path: Target location for encoded file.
        :type path: str or pathlike object.
        :param res: Target resolution (width, height) of video. Sum of pixels (width * height) must be divisible by 8. Defaults to (1920, 1080).
        :type res: tuple, optional
        :param bpp: Target 'bpp' of 'bits per pixel'. How many bits of information should be saved per pixel of video. Defaults to 2.
        :type bpp: int, optional
        :param framerate: XXXXXXXXXXXXXXXXXXX, defaults to 1.
        :type framrate: int, optional
        :param crf: XXXXXXXXXXXXXXXXXX, defaults to 0.
        :type crf: int, optional
        :param overwrite: Set to True to allow overwriting existing files. Defaults to False.
        :type overwrite: bool, optional
        :raises ValueError: If pixelsum of given argument res (width * height) is not divisible by 8.
        :raises ValueError: If argument crf is not in the range 0-52 inclusive.
        :raises ValueError: If argument bpp is an unsupported value.
        :raises FileNotFoundError: If argument path is an invalid filepath.
        :raises FileExistsError: If argument path points to an already existing file.
        """
        video_encoder = VideoEncoder(
            output = Path(path),
            framerate = framerate,
            res = res,
            crf = crf,
            overwrite = overwrite
        )
        arr = encode.load_array(self.input)
        arr = encode.add_lastframe_padding(arr, res, bpp)
        arr = encode.transform_array(arr, bpp)
        with video_encoder as video:
            video.feed(arr)
        self.metadata['bpp'] = bpp

    def encode_and_upload(self, res: tuple[int, int] = (1920, 1080), bpp: int = 2, framerate: int = 1, crf: int = 0) -> str:
        video_path = self.tempdir / 'encoded.mp4'
        self.encode(
            path = video_path,
            res = res,
            bpp = bpp,
            framereate = framerate,
            crf = crf
        )
        ## some upload stuff
        ## return url

    
class Decoder(TempDirMixin):

    def __init__(self, input: Union[str, Path]):
        if isinstance(input, str) and util.is_url(input):
            self.input = input
            self.input_type = 'url'
        elif Path(input).exists() and Path(input).is_file():
            self.input = Path(input)
            self.input_type = 'path'
        else:
            raise ValueError('A valid filepath or url must be passed, neither was found.')
        TempDirMixin.__init__(self)

    def decode(self, path: Union[str, Path], bpp: int = None, overwrite: bool = False):
        # bpp is autofilled if youbit also downloads the file.
        if self.input_type == 'url':
            #download video, to tempdir
            # file = downloaded video
            pass
        elif self.input_type == 'path':
            file = self.input
        video_decoder = VideoDecoder(vid = file)
        frames = []
        for frame in video_decoder:
            frame = decode.read_pixels(frame, bpp)
            frames.append(frame)
        arr = np.concatenate(frames, dtype=np.uint8)
        # decrypt and or unzip in-memory
        arr.tofile(Path(path)) ##TODO: overwrite logic here

    #def verify_checksum


# class YouBit:

#     def __init__(self, input: Union[str, Path]) -> None:
#         # add size constraints?
#         if util.is_url(input):
            
#             # prob get metadata as well imeeadiately?
#             # "etadata might change ebfore we download, downside
#             # we have access before calling download, upside
#             # what info do we need early? verify it is a youbit video, raise error else,  get metadata from description, should not change anyway. download specific info should be omitted.
#             self.input = input
#             self.input_type = 'url'
#         elif Path(input).exists():
#             if not input.is_file():
#                 raise ValueError('You must provide a file.')
#             if os.path.getsize(input) > 8000000000:
#                 raise ValueError('File too large. Only files up to 8GB are currently supported.')
#             self.input = Path(input)
#             self.input_type = 'file'
#             self.metadata = {
#                 'original_filename': self.input.name,
#                 'original_MD5': util.get_md5(self.input),
#             }
#         else:
#             if isinstance(input, PurePath):
#                 raise ValueError(f"No file was not found at '{str(input)}'.")
#             else:
#                 raise ValueError(f"Invalid input argument '{input}'. Must be a valid file location or valid URL.")
        

#         # Catch as many signals as possible to ensure _handle_exit() is called on exit.
#         atexit.register(self._handle_exit)
#         signal.signal(signal.SIGTERM, self._handle_exit)
#         signal.signal(signal.SIGINT, self._handle_exit)
    
#     def down(self, url: str, path: Union[str, Path], overwrite: bool = False) -> None:
#         """Downloads a YouBit video, decodes it, and saves it.
#         Check md5 by...
#         """
#         path = Path(path)
#         #...
#         self.output_path = path
#         ## we dont need to ask for bpp here since we can extract metadata from comments

#     def up(self, path: Union[str, Path], res: tuple[int, int] = (1920, 1080), bpp: int = 2, framerate: int = 1, crf: int = 0) -> str:
#         """Encodes a local file, and uploads that to YouTube."""
#         pass

#     # def decrypt() -> None:
#     #     pass
#     # maybe fake method which actually does nothing, but saves data so that other functions such as encode_local and down do encrypt/decrypt

#     # def encrypt():
#     #     pass

#     def encode_local(self, path: Union[str, Path], res: tuple[int, int] = (1920, 1080), bpp: int = 2, framerate: int = 1, crf: int = 0, overwrite: bool = False) -> None:
#         """Encodes a local file into a YouBit video.
        
#         :param path: Target location for encoded file.
#         :type path: str or pathlike object.
#         :param res: Target resolution (width, height) of video. Sum of pixels (width * height) must be divisible by 8. Defaults to (1920, 1080).
#         :type res: tuple, optional
#         :param bpp: Target 'bpp' of 'bits per pixel'. How many bits of information should be saved per pixel of video. Defaults to 2.
#         :type bpp: int, optional
#         :param framerate: XXXXXXXXXXXXXXXXXXX, defaults to 1.
#         :type framrate: int, optional
#         :param crf: XXXXXXXXXXXXXXXXXX, defaults to 0.
#         :type crf: int, optional
#         :param overwrite: Set to True to allow overwriting existing files. Defaults to False.
#         :type overwrite: bool, optional
#         :raises ValueError: If pixelsum of given argument res (width * height) is not divisible by 8.
#         :raises ValueError: If argument crf is not in the range 0-52 inclusive.
#         :raises ValueError: If argument bpp is an unsupported value.
#         :raises FileNotFoundError: If argument path is an invalid filepath.
#         :raises FileExistsError: If argument path points to an already existing file.
#         """
#         video_encoder = VideoEncoder(
#             output = Path(path),
#             framerate = framerate,
#             res = res,
#             crf = crf,
#             overwrite = overwrite
#         )
#         arr = encode.load_array(self.input)
#         arr = encode.add_lastframe_padding(arr, res, bpp)
#         arr = encode.transform_array(arr, bpp)
#         with video_encoder as video:
#             video.feed(arr)

#     def decode_local(self, path: Union[str, Path], bpp: int, overwrite: bool = False) -> None:
#         """Decodes a local YouBit video.

#         :param path: Target location for decoded file.
#         :type path: str or pathlike object.
#         :param bpp: The 'bpp' or Bits Per Pixel value that was used to encode the file originally.
#         :type bpp: int
#         :param overwrite: Set to True to allow overwriting existing files. Defaults to False.
#         :type overwrite: bool, optional
#         :raises FileNotFoundError: If argument path is an invalid filepath.
#         :raises FileExistsError: If argument path points to an already existing file.
#         """ ## bpp is only metadata requried, right now.
#         video_decoder = VideoDecoder(vid = self.input)
#         frames = []
#         for frame in video_decoder:
#             frame = decode.read_pixels(frame, bpp)
#             frames.append(frame)
#         arr = np.concatenate(frames, dtype=np.uint8)
#         path = Path(path)
#         arr.tofile(path)
#         self.output_path = path
        
#     def _handle_exit(self) -> None:
#         """Cleanup of temporary files."""
#         try:
#             shutil.rmtree(self._tempdir)
#         except:
#             pass

#     @property
#     def input_md5(self) -> str:
#         """Returns the MD5 checksum of the original file."""
#         return self.metadata.get('original_MD5')

#     @property
#     def output_md5(self) -> str:
#         """Returns the MD5 checksum of a decoded file. Can only be called after decoding a file."""




            
            







# class Encoder:

#     def __init__(self, file: Union[str, Path]) -> None:
#         """Accepts filepath string or Path object."""
#         if isinstance(file, PurePath):
#             self._original = file
#         else:
#             self._original = Path(file)
#         if self._original.exists():
#             if self._original.is_dir():
#                 raise ValueError('You must provide a file, not a directory.')
#             with open(str(self._original), 'rb') as f:
#                 filesize = os.fstat(f.fileno()).st_size
#                 if filesize > 8589934592:
#                     raise ValueError('Files over 8GiB are currently not supported.')
#                 md5 = hashlib.md5()
#                 while True:
#                     data = f.read(65560)
#                     if not data:
#                         break
#                     md5.update(data)
#                 self._metadata = {
#                     'original_MD5': str(md5.hexdigest()),
#                     'original_ext': str(self._original.suffix)
#                     }
#         else:
#             raise ValueError('File not found.')

#         # Catch as many signals as possible to ensure _handle_exit() is called on exit.
#         atexit.register(self._handle_exit)
#         signal.signal(signal.SIGTERM, self._handle_exit)
#         signal.signal(signal.SIGINT, self._handle_exit)

#         self._tempdir = tempfile.mkdtemp(prefix='youbit-')
#         self._zipped = self._tempdir / 'zipped.gz'
#         with open(str(self._original), 'rb') as f_in:
#             with gzip.open(str(self._zipped), 'wb') as f_out:
#                 shutil.copyfileobj(f_in, f_out)

#     def encrypt(self, pwd: str) -> None:
#         self._encrypted = self._tempdir / 'encrypted.aes'
#         pyAesCrypt.encryptFile(
#             str(self._zipped),
#             str(self._encrypted),
#             pwd
#             )
#         self._zipped.unlink()
#         self._metadata['encrypted'] = True

#     def encode(self, ecc: int = 20, bpp: int = 1, fps: int = 1):
#         apply_ecc(self.tempdir, ecc)
#         par_parity_size, par_recovery_size = make_frames(self.tempdir, bpp)
#         self._metadata['par_parity_size'] = par_parity_size
#         self._metadata['par_recovery_size'] = par_recovery_size
#         self._mp4 = make_video(self.tempdir, fps)
#         self._metadata['bpp'] = bpp
#         self._metadata['fps'] = fps

#     def upload(self, cookies_path: str, callback: Callable = None, headless: bool = False, cookie_cache: bool = True) -> None:
#         """
#         Upload video to YouTube using selenium chromedriver.
#         Requires manually provided cookies.
#         """
#         ##TODO: add cookie cache option, enabled by default, saves provided cookie file somewhere to reuse
#         ##TODO: even better, extract cookies programatically: https://www.thepythoncode.com/article/extract-chrome-cookies-python
#         uploader = Uploader(headless)
#         uploader.inject_cookies(cookies_path)
#         self.url = uploader.upload(
#             str(self._mp4) + '/yb-output.mp4',
#             'titlename', json.dumps(self._metadata),
#             callback, headless
#             )
#         self._handle_exit()

#     def save(self, path: Union[str, Path], readme: bool = True):
#         """
#         Saves the generated video and metadata for manual upload.
#         Set readme argument to False to not save a README.txt file.
#         """
#         ##TODO: save video, metadata.json, and optional readme.txt AND ZIP IT
#         ##TODO: check if path given is directory, in which case raise error or use default name, idk yet
#         if isinstance(path, PurePath):
#             location = path.parent / (path.name + '.zip')
#         else:
#             location = Path(path).parent / (Path(path).name + '.zip')
#         if self._original.exists():
#             if self._original.is_dir():
#                 raise ValueError('Please specify a filename too, not just a directory.')
#             readme_location = Path(__file__).parents[1].resolve() / 'data' / 'README_upload.txt'
#             with ZipFile(location, 'w') as zip:
#                 shutil.copy(readme_location, zip)
#                 json.dump(self._metadata, zip)
            

#         self._handle_exit()
    
#     def _handle_exit(self) -> None:
#         """Cleanup of temporary files."""
#         try:
#             shutil.rmtree(self._tempdir)
#         except:
#             pass

#     @property
#     def encrypted(self) -> bool:
#         """Returns boolean representing if the file was encrypted or not."""
#         if self._metadata.get('encrypted'):
#             return True
#         else:
#             return False

#     @property
#     def original(self) -> str:
#         """Returns the absolute path of the original file."""
#         return str(self._original)

#     @property
#     def md5(self) -> str:
#         """Returns the MD5 checksum of the original file."""
#         return self._metadata.get('MD5')

#     @property
#     def tempdir(self) -> str:
#         """Returns absolute path of temporary directory."""
#         return str(self._tempdir)

#     @property
#     def metadata(self) -> dict:
#         ##TODO: review this since I am not from sure this is te best way.
#         # return a copy of the metadata dictionary, because the original is not meant to be manually altered.
#         return self._metadata.copy()


# class Decoder:
    
#     def __init__(self, url: Union[str, Path]) -> None:
#         if isinstance(url, PurePath) and url.exists():
#             self._original = url
#         elif Path(url).exists():
#             self._original = Path(url)
#         else:
#             try:
#                 self._url = url
#                 self._yt = YouTube(self.url)
#                 self._stream = self.yt.streams.filter(adaptive=True, type='video')
#                 self._stream = self.stream.order_by('resolution').last() ##TODO: get 1080p secifically instead of highest res, in case that the video has not finished processing yet
#                 self._metadata = json.loads(self.yt.description.strip()) 
#             except:
#                 raise ValueError('Incorrect URL or video not available.') #TODO: check why VideoUnavailable wasnt recognized as exception, low priority

#         self._tempdir = tempfile.mkdtemp(prefix='youbit-')

#         # Catch as many signals as possible to ensure _handle_exit() is called on exit.
#         atexit.register(self._handle_exit)
#         signal.signal(signal.SIGTERM, self._handle_exit)
#         signal.signal(signal.SIGINT, self._handle_exit)

#     def download(self, callback = None) -> None:
#         if hasattr(self, '_url'):
#             self._stream.download(self._tempdir, filename='yb_download.mp4')
#         else:
#             raise ValueError('No URL was passed to the Decoder object.')

#     def decode(self) -> None:
#         ## TODO
#         extract_frames(self._tempdir)
#         extract_binary(self._tempdir,
#             self._metadata['par_parity_size'],
#             self._metadata['par_recovery_size'],
#             bpp=bpp)
#         remove_ecc(self._tempdir)

#     def decrypt(self, pwd: str) -> None:
#         if not self._metadata.get('encrypted'):
#             raise ValueError('This file was never encrypted during upload.')
#         pyAesCrypt.decryptFile(
#             str(self._tempdir) + '/extracted.aes',
#             str(self._tempdir) + 'extracted.bin',
#             pwd
#             )
#         # remove old .aes file
#         self._decrypted = True

#     def _check_checksum(self) -> None:
#         pass

#     def save(self, path: str) -> None:
#         _check_checksum()
#         # filepath with filename, but youbit will add original extension
#         if not hasattr(self, 'bin'):
#             raise ValueError('A file needs to be decoded first.')
#         elif self._metadata.get('encrypted') is True and not hasattr(self, 'decrypted'):
#             raise ValueError('This file was encrypted during upload, please decrypt it first.')
#         else:
#             file_ext = self._metadata.get('file_ext')
#             shutil.copy(self._extracted, Path(path + file_ext))
#             # self._handle_exit()

#     def _handle_exit(self) -> None:
#         try:
#             shutil.rmtree(self._tempdir)
#         except:
#             pass

#     @property
#     def original(self) -> str:
#         """Returns the original URL or file location."""
#         return str(self._original)

#     @property
#     def encrypted(self) -> bool:
#         if self._metadata.get('encrypted'):
#             return True
#         else:
#             return False


# if __name__ == '__main__':
#     pass

#     # yb = Encoder('E:/dev/youbit/data/test1.jpg')
#     # yb.to_video('E:/')