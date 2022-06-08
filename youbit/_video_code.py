from pathlib import Path
import av
import numpy as np
from typing import Union

class VideoEncoder:
    """1920x1080"""
    def __init__(self, output: Union[str, Path], framerate: int, res: tuple[int, int], crf: int, overwrite: bool = False) -> None:
        if crf not in range(0,53):
            raise ValueError(f'Invalid crf argument: {crf}. Must be between 0 and 52 inclusive.')
        output = Path(output)
        if output.exists() and output.is_file() and not overwrite:
            raise FileExistsError(f'File "{str(output)}" already exists.')
        self.container = av.open(str(output), mode='w')
        self.stream = self.container.add_stream("libx264", rate=framerate)
        self.stream.width = res[0]
        self.stream.height = res[1]
        self.stream.options = {'crf':str(crf), 'tune': 'grain', '-x264opts': 'no-deblock'}

    def feed(self, arr: np.ndarray[(1,), np.uint8]) -> None:
        ##TODO: validation, arr.reshape should work, if that works the rest of feed() works too. validate or is native numpy error clear enough?
        try:
            arr = arr.reshape(-1, self.stream.height, self.stream.width)
        except ValueError:
            raise ValueError(f'The length of the given array must be a multiple of the framesize, in this case {self.stream.width*self.stream.height} (= {self.stream.width} * {self.stream.height}).')
        for framearr in arr:
            frame = av.VideoFrame.from_ndarray(framearr, format='gray')
            self.container.mux(self.stream.encode(frame))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self.container.mux(self.stream.encode())
        self.container.close()


class VideoDecoder:
    """Only extracting keyframes
    only tested with yt yadda yadda"""
    def __init__(self, vid: Union[str, Path]) -> None:
        vid = Path(vid)
        if not vid.exists() or not vid.is_file():
            raise ValueError(f'File not found: {str(vid)}.')
        self.container = av.open(str(vid))
        self.stream = self.container.streams.video[0]
        # self.stream.thread_type = "AUTO"
        self.stream.codec_context.skip_frame = 'NONKEY'
        self.frames = self.container.decode(self.stream)

    def get_frame(self) -> np.ndarray[(1,), np.uint8]:
        frame = next(self.frames)
        if not ((frame.index-11) % 17): # The frames at index 11, 28, 45, 64... (the 12th + interval of 17) are duplicate keyframes and must be skipped. 
            frame = next(self.frames)
        frame = frame.to_ndarray(format='gray').ravel()
        return frame

    def __iter__(self):
        return self

    def __next__(self) -> np.ndarray[(1,), np.uint8]:
        try:
            return self.get_frame()
        except StopIteration as e:
            self.close()
            raise e
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.container.close()