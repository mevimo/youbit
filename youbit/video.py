from pathlib import Path
from typing import Any, Union, Tuple
import warnings
from itertools import islice

import av
import numpy as np

from youbit.types import ndarr_1d_uint8


class VideoEncoder:
    """1920x1080"""

    def __init__(
        self,
        output: Union[str, Path],
        framerate: int = 1,
        res: Tuple[int, int] = (1920, 1080),
        crf: int = 0,
        zero_frame: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Initializes the encoder with all the required settings. Uses x264 encoding.

        :param output: Where to write the encoded video to.
        :type output: str or Path
        :param framerate: The desired video framerate, defaults to 1
        :type framerate: int, optional
        :param res: The desired video resolution, defaults to (1920, 1080)
        :type res: tuple[int, int], optional
        :param crf: The desired 'crf' or 'Constant Rate Factor' to use during encoding, defaults to 0
        :type crf: int, optional
        :param overwrite: Whether or not allow overwriting existing files, defaults to False
        :type overwrite: bool, optional
        :param zero_frames: How many 'zero frames' to inject between every real frame.
            Zero frames are completely black frames, all zeros, defaults to 0
        :type zero_frames: int, optional
        :raises ValueError: If argument 'crf' is not between 0 and 52 inclusive
        :raises FileExistsError: If 'output' path specified already has an existing file, and the 'overwrite' argument is set to False
        """
        if crf not in range(0, 53):
            raise ValueError(
                f"Invalid crf argument: {crf}. Must be between 0 and 52 inclusive."
            )
        output = Path(output)
        if output.exists() and output.is_file() and not overwrite:
            raise FileExistsError(f'File "{str(output)}" already exists.')
        self.container = av.open(str(output), mode="w")
        self.stream = self.container.add_stream("libx264", rate=framerate)
        self.stream.width = res[0]
        self.stream.height = res[1]
        self.framesize = res[0] * res[1]
        self.stream.options = {
            "crf": str(crf),
            "tune": "grain",
            "-x264opts": "no-deblock",
        }
        self.zero_frame = zero_frame
        if self.zero_frame:
            self.zero_array = np.zeros(
                (self.stream.height, self.stream.width), np.uint8
            )
        self.cache = np.empty(0, dtype=np.uint8)

    def feed(self, arr: ndarr_1d_uint8) -> None:
        """Feeds uint8 numpy arrays where each element represents one pixel, to
        the video encoder. If the given array is not a factor of framesize, the
        surplus elements are cached and used on the next call to feed.

        :param arr: The input array
        :type arr: 1 dimensional uin8 numpy array
        """
        if self.cache.size:
            arr = np.append(self.cache, arr)
            self.cache = np.empty(0, dtype=np.uint8)
        if surplus := (arr.size % self.framesize):
            self.cache = arr[-surplus:]
            arr = arr[:-surplus]
        arr = arr.reshape(-1, self.stream.height, self.stream.width)
        for framearr in arr:
            frame = av.VideoFrame.from_ndarray(framearr, format="gray")
            self.container.mux(self.stream.encode(frame))
            if self.zero_frame:
                frame = av.VideoFrame.from_ndarray(self.zero_array, format="gray")
                self.container.mux(self.stream.encode(frame))

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()

    def close(self) -> None:
        """If cache is not empty, close() will add zero's to the cache so it
        matches the framesize, before encoding that (last) frame and closing
        the container.
        """
        if self.cache.size:
            padding = self.framesize - (self.cache.size % self.framesize)
            padding_arr = np.zeros(padding, dtype=self.cache.dtype)
            frame_arr = np.append(self.cache, padding_arr)
            self.cache = np.empty(0, dtype=np.uint8)
            self.feed(frame_arr)
            assert not self.cache.size
        self.container.mux(self.stream.encode())
        self.container.close()


class VideoDecoder:
    """Only extracting keyframes
    only tested with yt yadda yadda
    WONT WORK WHEN THE VIDEO HAS NOT YET PASSED THROUGH YOUTUBE
    """

    def __init__(self, vid: Union[str, Path], zero_frame: bool = False) -> None:
        vid = Path(vid)
        if not vid.exists() or not vid.is_file():
            raise ValueError(f"File not found: {str(vid)}.")
        self.container = av.open(str(vid))
        self.stream = self.container.streams.video[0]
        if self.stream.codec_context.framerate == 1:
            warnings.warn(
                f"Video passed to {type(self).__name__} has a framerate of 1. "
                "This probably means the video did not go though YouTube. "
                "Beware that this decoder will only work on videos that have "
                "gone through YouTube's own compression."
            )
        self.framesize = (
            self.stream.codec_context.height * self.stream.codec_context.width
        )
        # self.stream.thread_type = "AUTO" # seems to not help :(
        self.stream.codec_context.skip_frame = "NONKEY"
        if zero_frame:
            self.frames = islice(self.container.decode(self.stream), 0, None, 2)
        else:
            self.frames = self.container.decode(self.stream)
        self.cache = np.empty(0, dtype=np.uint8)

    def get_array(self, length) -> ndarr_1d_uint8:
        """Extracts (length) pixels from the video, returning a numpy uint8 ndarray
        where each element represents one pixel.
        This still uses the get_frame() method, calling it as many times as is
        needed to extract the given amount of pixels. A cache is kept of pixels
        that have been decoded by get_frame() but have not yet been returned
        by this function. Abstracts frames away.
        """
        frame_count = -((length - self.cache.size) / -self.framesize)
        if self.cache.size:
            frames = [self.cache]
            self.cache = np.empty(0, dtype=np.uint8)
        else:
            frames = []
        for _ in range(frame_count):
            try:
                frames.append(self.get_frame())
            except StopIteration:
                break
        if len(frames) == 0:
            return np.empty(0, dtype=np.uint8)
        arr = np.concatenate(frames, dtype=np.uint8)

        if arr.size > length:
            surplus = arr.size - length
            self.cache = arr[-surplus:]
            arr = arr[:-surplus] 
        return arr

    def get_frame(self) -> ndarr_1d_uint8:
        """Reads 1 frame of the video, returning it as a numpy uint8 array.
        Properly skips over duplicate keyframes. It does this by simply filtering
        out certain indexes. We could also compare the current frame to the next
        to see if they are similar (enough) to be considered duplicates, but this
        process would be very time complex and possibly inconsistent.
        Because we use known indexes, this only works when the video has passed
        through YouTube, where it was re-encoded from 1 fps to 6.
        """
        frame: Any = next(self.frames)
        if not (
            (frame.index - 11) % 17
        ):  # The frames at index 11, 28, 45, 64... (the 12th + interval of 17) are duplicate keyframes and must be skipped.
            frame = next(self.frames)
        arr: ndarr_1d_uint8 = frame.to_ndarray(format="gray").ravel()
        return arr

    def __iter__(self) -> Any:
        return self

    def __next__(self) -> ndarr_1d_uint8:
        try:
            return self.get_frame()
        except StopIteration as e:
            self.close()
            raise e

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()

    def close(self) -> None:
        self.container.close()
