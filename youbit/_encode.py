from ast import Raise
import cv2
import subprocess
import numpy as np
from pathlib import Path
from par2deep.par2deep import par2deep
import shutil
import os
import av
import time
from numba import njit, prange


##TODO: Disable more filters @ video encoder
##TODO: chunking....


def apply_ecc_par(tempdir: Path) -> tuple[Path, int, int]:
    """
    Will create a parity file, and a file with recovery blocks in the given directory,
    using par2.
    PC argument specifies the percentage of data BLOCKS that may be corrupted before
    data can no longer be recreated.
    """
    # par2deep was designed for CLI use, not like this, hence the weirdness.
    # This tool is TEMPORARY, it is very limited since i can only set a 'percentage'
    # for error resiliency, but I have no control over block size.
    # Block size is set to whatever creates a source block count of 2000, with 72 as a minimum.
    # This means block size can easily become massive for larger files, which is okay for bad
    # sectors on a HDD, but not particulary great for the kind of small error streaks we see
    # in this application.
    # I might have to consider a non library multi-platform application with CLI support,
    # just ship youbit with the binaries, and interface with it via subprocess.Popen()...
    ## TODO: switch to par2.exe subprocess
    par = par2deep(str(tempdir))
    par.args['quiet'] = True
    par.args['percentage'] = pc
    par.args['clean_backup'] = True
    par.check_state()
    for _ in par.execute(): pass

    # -----------------------------------------------------------
    for file in tempdir.iterdir():
        if 'vol' in file.name and file.suffix == '.par2':
            par_recovery = file
            par_recovery_size = os.path.sizeof(par_recovery)
        elif file.suffix == '.par2':
            par_parity = file
            par_parity_size = os.path.sizeof(par_parity)
        else:
            par_main = file
    with open(par_parity, 'ab') as parity, open(par_recovery, 'rb') as recovery, open(par_main, 'rb') as main:
        # We want it in order; parity -> recovery -> main
        shutil.copyfileobj(recovery, parity)
        shutil.copyfileobj(main, parity)
    file = par_parity.rename(par_parity.parent / 'file.bin')
    par_recovery.unlink()
    par_main.unlink()
    return file, par_parity_size, par_recovery_size


def apply_ecc_polar():
    ##TODO: cython extension for aff3ct lib, if possible
    pass


def add_lastframe_padding(arr: np.ndarray, res: tuple[int, int], bpp: int) -> np.ndarray:
    framesize = int(res[0] * res[1] / 8 * bpp)
    last_frame_padding = framesize - (arr.size % framesize)
    if last_frame_padding:
        arr = np.append(arr, np.zeros(last_frame_padding, dtype=np.uint8))
    return arr


@njit('void(uint8[::1], uint8[::1], uint8[::1])', inline='never')
def _numba_transform_bpp3_x64(arr, out, mapping):
    for i in range(64):
        j = i * 3
        out[i] = mapping[(arr[j]<<2)|(arr[j+1]<<1)|(arr[j+2])]


@njit('void(uint8[::1], int_, uint8[::1], uint8[::1])', parallel=True)
def _numba_transform_bpp3(arr, div, out, mapping):
    for i in prange(div//64):
        _numba_transform_bpp3_x64(arr[i*192:(i*192)+192], out[i*64:(i*64)+64], mapping)


@njit('void(uint8[::1], uint8[::1], uint8[::1])', inline='never')
def _numba_transform_bpp2_x64(arr, out, mapping):
    for i in range(64):
        j = i * 2
        out[i] = mapping[(arr[j]<<1)|(arr[j+1])]


@njit('void(uint8[::1], int_, uint8[::1], uint8[::1])', parallel=True)
def _numba_transform_bpp2(arr, div, out, mapping):
    for i in prange(div//64):
        _numba_transform_bpp2_x64(arr[i*128:(i*128)+128], out[i*64:(i*64)+64], mapping)


def transform_array(arr: np.ndarray, bpp: int) -> np.ndarray:
    """Transforms a uint8 numpy array (0, 255, 38, ..) representing individual bytes
    into a uint8 numpy array representing 8 bit greyscale pixels. Returns a new array.
    The output depends on the 'bpp' (or 'bits per pixel') parameter.

    A 'bpp' of 1 for example, dictates each pixel should hold the information of 
    a single bit. A bit has 2 possible states, 1 and 0, so our corresponding pixel
    should too. The pixel will be either 0 or 255 (black and white) to represent
    0 and 1 respectively.

    A 'bpp' of 3 thus means 3 bits of information in every pixel.
    Since 3 bits have 8 possible combinations (000,001,010,011,100,101,110,111),
    our pixel will need 8 distinct states as well (0,48,80,112,144,176,208,255) 
    to represent the 3 bits.

    It does this by first unpacking the array into a binary representation of it
    (essentially converting from decimal to binary, 65 -> 01000001).
    It then groups consecutive binary digits into groups of 3, before mapping
    these triplets to an appropriate pixel value.

    This function expects the length of the input array to be divisible, without
    remainder, by the bpp as well as bpp*8.
    This works on products of the pixel sum of common resolutions (1080,720p,4k...),
    so long as padding for the last frame was added to the array before transforming it,
    this requirement will be satisfied.
    """
    if arr.size % bpp:
        raise ValueError(f'The length of the given array ({arr.size}) is not divisible by the given bpp ({bpp}).')
    if arr.size % (bpp*8):
        raise ValueError(f'The length of the given array ({arr.size}) is not divisible by the given bpp * 8 ({(bpp*8)}).')
    arr = np.unpackbits(arr)
    div = int(arr.size / bpp)
    out = np.zeros(div, dtype=np.uint8)
    if bpp == 1:
        mapping = np.array([0,255], dtype=np.uint8)
        out = mapping[arr]
    elif bpp == 2:
        mapping = np.array([0,96,160,255], dtype=np.uint8)
        _numba_transform_bpp2(arr, div, out, mapping)
    elif bpp == 3:
        mapping = np.array([0,48,80,112,144,176,208,255], dtype=np.uint8)
        _numba_transform_bpp3(arr, div, out, mapping)
    elif bpp == 8:
        raise ValueError('A bpp of 8 was passed as argument. No transformation is required when using a bpp of 8.')
    else:
        raise ValueError(f'Unsupported bpp argument: {bpp} of type {type(bpp)}.')
    return out


class VideoEncoder:
    """1920x1080"""
    def __init__(self, output: Path, framerate: int, res: tuple[int, int], crf: int):
        ##TODO: validate crf to be within possible values
        ##TODO: raise error when output file path already exists, unless 'overwrite' parameter or something is set to true
        self.container = av.open(str(output), mode='w')
        self.stream = self.container.add_stream("libx264", rate=framerate)
        self.stream.width = res[0]
        self.stream.height = res[1]
        self.stream.options = {'crf':str(crf), 'tune': 'grain', '-x264opts': 'no-deblock'}
    def feed(self, arr):
        ##TODO: validation, arr.reshape should work, if that works the rest of feed() works too. validate or is native numpy error clear enough?
        arr = arr.reshape(-1, self.stream.height, self.stream.width)
        for framearr in arr:
            frame = av.VideoFrame.from_ndarray(framearr, format='gray')
            self.container.mux(self.stream.encode(frame))
    def finish(self):
        self.container.mux(self.stream.encode())
        self.container.close()


# def video_encode(arr: np.ndarray, output: Path, framerate: int, res: tuple[int, int], crf: int) -> None:
#     """1920x1080"""
#     arr = arr.reshape(-1, res[1], res[0])
#     container = av.open(str(output), mode='w')
#     stream = container.add_stream("libx264", rate=framerate)
#     stream.width = res[0]
#     stream.height = res[1]
#     stream.options = {'crf':str(crf), 'tune': 'grain', '-x264opts': 'no-deblock'}
#     # stream.options = {'crf': '20', 'tune': 'grain', '-x264opts': 'no-deblock'}
#     for framearr in arr:
#         frame = av.VideoFrame.from_ndarray(framearr, format='gray')
#         container.mux(stream.encode(frame))
#     container.mux(stream.encode())
#     container.close()

    
# def encode(file: Path, output: Path, bpp: int = 3, framerate: int = 1, crf: int = 0) -> None:
#     """IDK EXPLAIN

#     :param file: Path object of the file in question.
#     :type file: Path
#     :param bpp: 'Bits Per Pixel', how many bits to encode per
#         pixel. The higher the value, the higher the chance of
#         corruption during compression.
#     :type bpp: int
#     :raises ValueError: if the value of the 'bpp' argument is
#         not currently supported.
#     """
#     if bpp == 1:
#         mapping = np.array([0,255], dtype=np.uint8)
#     elif bpp == 2:
#         mapping = np.array([0,160,96,255], dtype=np.uint8)
#     elif bpp == 3:
#         # mapping = np.array([0,144,80,208,48,176,112,255], dtype=np.uint8)
#         mapping = np.array([0,48,80,112,144,176,208,255], dtype=np.uint8)
#     else:
#         raise ValueError('Unsupported BPP (Bits Per Pixel) value.')

#     start = time.time()
#     print(f'start: {start}')
#     bin = np.fromfile(file, dtype=np.uint8)
#     tok = time.time()
#     print(f'Finished loading file: {time.time() - start}')
#     framesize = 259200 * bpp
#     last_frame_padding = framesize - (bin.size % framesize)
#     if last_frame_padding:
#         bin = np.append(bin, np.zeros(last_frame_padding, dtype=np.uint8))
#     framecount = int(bin.size / framesize)

#     print(f'finished padding, starting unpackbits: {time.time() - start}')
#     bin = np.unpackbits(bin)
#     print(f'Unpacked bits: {time.time() - start}')
#     if bpp > 1:
#         bin = np.packbits(bin, axis=1, bitorder='little').ravel()
#         # bin = numba_packbits(bin)
#     print(f'packed bits: {time.time() - start}')
#     bin = mapping[bin]
#     print(f'FINISHED MAPPING: {time.time() - start}')
#     bin = bin.reshape(framecount, 1080, 1920)

#     print(f'finished reshape, starting container.... {time.time() - start}')
#     container = av.open(str(output), mode='w')
#     stream = container.add_stream("libx264", rate=framerate)
#     stream.width = 1920
#     stream.height = 1080
#     stream.options = {'crf':str(crf), 'tune': 'grain', '-x264opts': 'no-deblock'}
#     # stream.options = {'crf': '20', 'tune': 'grain', '-x264opts': 'no-deblock'}
#     print(f'Starting encoding loop: {time.time() - start}')
#     for binframe in bin:
#         frame = av.VideoFrame.from_ndarray(binframe, format='gray')
#         container.mux(stream.encode(frame))
#     print(f'Finished encoding loop, closing container now: {time.time() - start}')
#     container.mux(stream.encode())
#     container.close()


