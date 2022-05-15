from ast import Raise
import cv2
import subprocess
import numpy as np
from pathlib import Path
from par2deep.par2deep import par2deep
import shutil
import os
import av


def apply_ecc(tempdir: Path) -> tuple[Path, int, int]:
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
    ## TODO: switch to par2.dll control via ctypes, package youbit with binaries for linux and windows
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
    

def encode(file: Path, output: Path, bpp: int, framerate: int = 1, crf: int = 0) -> None:
    """IDK EXPLAIN

    :param file: Path object of the file in question.
    :type file: Path
    :param bpp: 'Bits Per Pixel', how many bits to encode per
        pixel. The higher the value, the higher the chance of
        corruption during compression.
    :type bpp: int
    :raises ValueError: if the value of the 'bpp' argument is
        not currently supported.
    """
    ## TODO: chunking, reading each file out in chunks, big loop, create 1 frame each loop.
    ## TODO: mulitprocessing
    if bpp == 1:
        mapping = np.array([0,255], dtype=np.uint8)
    elif bpp == 2:
        mapping = np.array([0,160,96,255], dtype=np.uint8)
    elif bpp == 3:
        mapping = np.array([0,144,80,208,48,176,112,255], dtype=np.uint8)
    else:
        raise ValueError('Unsupported BPP (Bits Per Pixel) value.')

    bin = np.fromfile(file, dtype=np.uint8)
    framesize = 259200 * bpp
    last_frame_padding = framesize - (bin.size % framesize)
    if last_frame_padding:
        bin = np.append(bin, np.zeros(last_frame_padding, dtype=np.uint8))
    framecount = int(bin.size / framesize)

    bin = np.unpackbits(bin).reshape(-1,bpp)
    if bpp > 1:
        bin = np.packbits(bin, axis=1, bitorder='little').ravel()
    bin = mapping[bin]
    bin = bin.reshape(framecount, 1080, 1920)

    container = av.open(str(output), mode='w')
    stream = container.add_stream("libx264", rate=framerate)
    stream.width = 1920
    stream.height = 1080
    stream.options = {'crf':str(crf)}
    # stream.options = {'crf': '20', 'tune': 'grain', '-x264opts': 'no-deblock'}
    for binframe in bin:
        frame = av.VideoFrame.from_ndarray(binframe, format='gray')
        container.mux(stream.encode(frame))
    container.mux(stream.encode())
    container.close()
