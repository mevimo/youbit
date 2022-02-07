from __future__ import annotations
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

from youbit.upload import Uploader
from youbit.encode import apply_ecc, make_frames, make_video
from youbit.decode import remove_ecc, extract_frames, extract_binary


class Encoder:

    def __init__(self, file: Union[str, Path]) -> None:
        """Accepts filepath string or Path object."""
        if isinstance(file, PurePath):
            self._original = file
        else:
            self._original = Path(file)
        if self._original.exists():
            if self._original.is_dir():
                raise ValueError('You must provide a file, not a directory.')
            with open(str(self._original), 'rb') as f:
                filesize = os.fstat(f.fileno()).st_size
                if filesize > 8589934592:
                    raise ValueError('Files over 8GiB are currently not supported.')
                md5 = hashlib.md5()
                while True:
                    data = f.read(65560)
                    if not data:
                        break
                    md5.update(data)
                self._metadata = {
                    'MD5': str(md5.hexdigest()),
                    'original_ext': str(self._original.suffix)
                    }
        else:
            raise ValueError('File not found.')

        # Catch as many signals as possible to ensure _handle_exit() is called on exit.
        atexit.register(self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)

        self._tempdir = tempfile.mkdtemp(prefix='youbit-')
        self._zipped = self._tempdir / 'zipped.gz'
        with open(str(self._original), 'rb') as f_in:
            with gzip.open(str(self._zipped), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def encrypt(self, pwd: str) -> None:
        self._encrypted = self._tempdir / 'encrypted.aes'
        pyAesCrypt.encryptFile(
            str(self._zipped),
            str(self._encrypted),
            pwd
            )
        self._zipped.unlink()
        self._metadata['encrypted'] = True

    def encode(self, ecc: int = 20, bpp: int = 1, fps: int = 1):
        apply_ecc(self.tempdir, ecc)
        par_parity_size, par_recovery_size = make_frames(self.tempdir, bpp)
        self._metadata['par_parity_size'] = par_parity_size
        self._metadata['par_recovery_size'] = par_recovery_size
        make_video(self.tempdir, fps)
        self._metadata['bpp'] = bpp
        self._metadata['fps'] = fps

    def upload(self, cookies_path: str, callback: Callable = None, headless: bool = False, cookie_cache: bool = True) -> None:
        """
        Upload video to YouTube using selenium chromedriver.
        Requires manually provided cookies.
        """
        ##TODO: add cookie cache option, enabled by default, saves provided cookie file somewhere to reuse
        ##TODO: even better, extract cookies programatically: https://www.thepythoncode.com/article/extract-chrome-cookies-python
        uploader = Uploader(headless)
        uploader.inject_cookies(cookies_path)
        self.url = uploader.upload(
            str(self.__tempdir) + '/yb-output.mp4',
            'titlename', json.dumps(self._metadata),
            callback, headless
            )
        self._handle_exit()

    def save(self, path, readme: bool = True):
        """
        Saves the generated video and metadata for manual upload.
        Set readme argument to False to not save a README.txt file.
        """
        ##TODO: save video, metadata.json, and optional readme.txt AND ZIP IT
        ##TODO: check if path given is directory, in which case raise error or use default name, idk yet
        self._handle_exit()
    
    def _handle_exit(self) -> None:
        """Cleanup of temporary files."""
        try:
            shutil.rmtree(self._tempdir)
        except:
            pass

    @property
    def encrypted(self) -> bool:
        """Returns boolean representing if the file was encrypted or not."""
        if self._metadata.get('encrypted'):
            return True
        else:
            return False

    @property
    def original(self) -> str:
        """Returns the absolute path of the original file."""
        return str(self._original)

    @property
    def md5(self) -> str:
        """Returns the MD5 checksum of the original file."""
        return self._metadata.get('MD5')

    @property
    def tempdir(self) -> str:
        """Returns absolute path of temporary directory."""
        return str(self._tempdir)

    @property
    def metadata(self) -> dict:
        ##TODO: review this since I am not from sure this is te best way.
        # return a copy of the metadata dictionary, because the original is not meant to be manually altered.
        return self._metadata.copy()


class Decoder:
    
    def __init__(self, url: Union[str, Path]) -> None:
        if isinstance(url, PurePath) and url.exists():
            self._original = url
        elif Path(url).exists():
            self._original = Path(url)
        else:
            try:
                self._url = url
                self._yt = YouTube(self.url)
                self._stream = self.yt.streams.filter(adaptive=True, type='video')
                self._stream = self.stream.order_by('resolution').last() ##TODO: get 1080p secifically instead of highest res, in case that the video has not finished processing yet
                self._metadata = json.loads(self.yt.description) 
            except:
                raise ValueError('Incorrect URL or video not available.') #TODO: check why VideoUnavailable wasnt recognized as exception, low priority

        self._tempdir = tempfile.mkdtemp(prefix='youbit-')

        # Catch as many signals as possible to ensure _handle_exit() is called on exit.
        atexit.register(self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)

    def download(self, callback = None) -> None:
        if hasattr(self, '_url'):
            self._stream.download(self._tempdir, filename='yb_download.mp4')
        else:
            raise ValueError('No URL was passed to the Decoder object.')

    def decode(self) -> None:
        ## TODO
        extract_frames(self._tempdir)
        extract_binary(self._tempdir,
            self._metadata['par_parity_size'],
            self._metadata['par_recovery_size'],
            bpp=bpp)
        remove_ecc(self._tempdir)

    def decrypt(self, pwd: str) -> None:
        if not self._metadata.get('encrypted'):
            raise ValueError('This file was never encrypted during upload.')
        pyAesCrypt.decryptFile(
            str(self._tempdir) + '/extracted.aes',
            str(self._tempdir) + 'extracted.bin',
            pwd
            )
        # remove old .aes file
        self._decrypted = True

    def _check_checksum(self) -> None:
        pass

    def save(self, path: str) -> None:
        _check_checksum()
        # filepath with filename, but youbit will add original extension
        if not hasattr(self, 'bin'):
            raise ValueError('A file needs to be decoded first.')
        elif self._metadata.get('encrypted') is True and not hasattr(self, 'decrypted'):
            raise ValueError('This file was encrypted during upload, please decrypt it first.')
        else:
            file_ext = self._metadata.get('file_ext')
            shutil.copy(self._extracted, Path(path + file_ext))
            # self._handle_exit()

    def _handle_exit(self) -> None:
        try:
            shutil.rmtree(self._tempdir)
        except:
            pass

    @property
    def original(self) -> str:
        """Returns the original URL or file location."""
        return str(self._original)

    @property
    def encrypted(self) -> bool:
        if self._metadata.get('encrypted'):
            return True
        else:
            return False


if __name__ == '__main__':
    pass

    # yb = Encoder('E:/dev/youbit/data/test1.jpg')
    # yb.to_video('E:/')