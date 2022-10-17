"""
Houses the VideoEncoder and VideoDecoder class, to encode arrays into
YouBit video's and decode those back into arrays respectively.
"""
from pathlib import Path
from typing import Any, Union, Generator
import warnings
from itertools import islice

import av
import numpy as np

from youbit.types import ndarr_1d_uint8
from youbit.settings import Settings


class VideoEncoder:

    def __init__(self, output: Path, settings: Settings) -> None:
        self.cache = np.empty(0, dtype=np.uint8)
        self.null_frames = settings.null_frames
        self.container = av.open(str(output), mode="w")
        self.stream = self.container.add_stream("libx264", rate=1)
        self.stream.width, self.stream.height = settings.resolution.value
        self.framesize = self.stream.width * self.stream.height
        self.stream.options = {
            "crf": str(settings.constant_rate_factor),
            "tune": "grain",
            "-x264opts": "no-deblock",
        }

    def feed(self, arr: ndarr_1d_uint8) -> None:
        """Each element of the input array is expected to represent one geyscale pixel.
        """
        arr_of_frames = self._prepare_array(arr)
        for frame in arr_of_frames:
            av_frame = av.VideoFrame.from_ndarray(frame, format="gray")
            self.container.mux(self.stream.encode(av_frame))
            if self.null_frames:
                self._inject_null_frame()

    def _prepare_array(self, arr_correct_size: ndarr_1d_uint8) -> np.ndarray:
        arr_with_cache = self._prepend_cache_to(arr_correct_size)
        arr_correct_size = self._cache_surplus_elem_from(arr_with_cache)
        reshaped_arr = arr_correct_size.reshape(-1, self.stream.height, self.stream.width)
        return reshaped_arr

    def _prepend_cache_to(self, arr: ndarr_1d_uint8) -> ndarr_1d_uint8:
        if self.cache.size:
            new_arr = np.append(self.cache, arr)
            self.cache = np.empty(0, dtype = np.uint8)
            return new_arr
        return arr

    def _cache_surplus_elem_from(self, arr: ndarr_1d_uint8) -> ndarr_1d_uint8:
        """Any elements at the end of the array that cannot form a complete
        frame, are removed and cached."""
        if surplus := (arr.size % self.framesize):
            self.cache = arr[-surplus:]
            arr = arr[:-surplus]
        return arr

    def _inject_null_frame(self) -> None:
        null_frame = np.zeros(
            (self.stream.height, self.stream.width), np.uint8
        )
        frame = av.VideoFrame.from_ndarray(null_frame, format="gray")
        self.container.mux(self.stream.encode(frame))

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()

    def close(self) -> None:
        """Flushes the cache and closes the container. Must happen!
        """
        if self.cache.size:
            padding_size = self.framesize - (self.cache.size % self.framesize)
            padding_arr = np.zeros(padding_size, dtype=self.cache.dtype)
            self.feed(padding_arr)
            assert not self.cache.size

        self.container.mux(self.stream.encode())
        self.container.close()


class VideoDecoder:
    """Only works on videos downloaded from YouTube, and whose codec is supported.
    Supports h264 and vp9."""

    def __init__(self, input_file: Path, settings: Settings) -> None:
        self.container = av.open(str(input_file))
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
        self.frames = self._create_frame_generator()
        if settings.null_frames:
            self.frames = islice(self.frames, None, None, 2)
        self.cache = np.empty(0, dtype=np.uint8)

    def extract_pixeldata(self, amount_of_pixels: int) -> ndarr_1d_uint8:
        """Can return less than the requested amount of pixeldata
        (down to an empty array) if there is no more data to extract.
        """
        frames = []
        if self.cache.size:
            frames.append(self.cache)
            self.cache = np.empty(0, dtype=np.uint8)

        frames_to_extract = -((amount_of_pixels - self.cache.size) // -self.framesize)
        for _ in range(frames_to_extract):
            try:
                frames.append(next(self.frames))
            except StopIteration:
                break
        
        if len(frames) == 0:
            return np.empty(0, dtype=np.uint8)
        arr = np.concatenate(frames, dtype=np.uint8)

        if arr.size > amount_of_pixels:
            surplus = arr.size - amount_of_pixels
            self.cache = arr[-surplus:]
            arr = arr[:-surplus]
        return arr

    def _create_frame_generator(self) -> Generator[np.ndarray, None, None]:
        if self.stream.codec_context.codec.name == "h264":
            self.stream.codec_context.skip_frame = "NONKEY"
            frames = self.container.decode(self.stream)
            frame_generator = (
                frame.to_ndarray(format="gray").ravel()
                for frame in frames
                if (frame.index - 11) % 17  # skipping duplicate keyframes
            )
        elif self.stream.codec_context.codec.name == "vp9":
            frames = self.container.decode(self.stream)
            frames = islice(self.frames, None, None, 6)
            frame_generator = (
                frame.to_ndarray(format="gray").ravel()
                for frame in frames
            )
        else:
            raise RuntimeError(
                f"Video has an unsupported codec: {self.stream.codec_context.codec.name}"
            )
        return frame_generator

    def __iter__(self) -> Any:
        return self.frames

    def __next__(self) -> ndarr_1d_uint8:
        try:
            return next(self.frames)
        except StopIteration as e:
            self.close()
            raise e

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: str, **kwargs: str) -> None:
        self.close()

    def close(self) -> None:
        """Closes the video container."""
        self.container.close()
