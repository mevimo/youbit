from pathlib import Path
import av
import numpy as np


class VideoEncoder:
    """1920x1080"""
    def __init__(self, output: Path, framerate: int, res: tuple[int, int], crf: int, overwrite: bool = False) -> None:
        if crf not in range(0,53):
            raise ValueError(f'Invalid crf argument: {crf}. Must be between 0 and 52 inclusive.')
        if output.exists() and output.is_file() and not overwrite:
            raise FileExistsError(f'File "{str(output)}" already exists.')
        self.container = av.open(str(output), mode='w')
        self.stream = self.container.add_stream("libx264", rate=framerate)
        self.stream.width = res[0]
        self.stream.height = res[1]
        self.stream.options = {'crf':str(crf), 'tune': 'grain', '-x264opts': 'no-deblock'}

    def feed(self, arr) -> None:
        ##TODO: validation, arr.reshape should work, if that works the rest of feed() works too. validate or is native numpy error clear enough?
        arr = arr.reshape(-1, self.stream.height, self.stream.width)
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
    """Only extracting keyframes"""
    def __init__(self, vid: Path) -> None:
        if not vid.exists() or not vid.is_file():
            raise ValueError(f'File not found: {str(vid)}.')
        self.container = av.open(str(vid))
        self.stream = self.container.streams.video[0]
        # self.stream.thread_type = "AUTO"
        self.stream.codec_context.skip_frame = 'NONKEY'
        print(self.stream.frames)
        self.frames = self.container.decode(self.stream)

    def get_frame(self) -> np.ndarray:
        frame = next(self.frames)
        print(frame.index, frame.pict_type)
        frame = frame.to_ndarray(format='gray').ravel()
        return frame

    def __iter__(self):
        return self

    def __next__(self) -> np.ndarray:
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