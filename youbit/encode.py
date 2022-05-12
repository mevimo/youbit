from ast import Raise
import cv2
import subprocess
import numpy as np
from pathlib import Path
from par2deep.par2deep import par2deep
import shutil
import os


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


def make_frames(file: Path, bpp: int) -> None:
    """Takes Path to the file in question as an argument, and encodes
    the binary information to a series of greyscale png images.
    These images are saved to the directory of the given file,
    using the ordered naming convention 'frame1.png'.
    The given file is deleted.

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
        mapping = np.array([0,255])
    elif bpp == 2:
        mapping = np.array([0,160,96,255])
    elif bpp == 3:
        mapping = np.array([0,144,80,208,48,176,112,255])
    else:
        raise ValueError('Unsupported BPP (Bits Per Pixel) value.')

    bin = np.fromfile(str(file), dtype=np.uint8)
    # NOTE: Trailing null bytes on a gzip does not affect its checksum.
    framesize = 259200 * bpp
    filler_bytes = framesize - (bin.size // framesize)
    if filler_bytes != 0:
        zeros = np.zeros(filler_bytes, dtype=np.uint8)
        bin = np.append(bin, zeros)
        del zeros
    framecount = bin.size // framesize

    for i in range(framecount):
        start = framesize * i
        stop = start + framesize
        frame = np.unpackbits(bin[start:stop]).reshape(-1,bpp)
        if bpp > 1:
            frame = np.packbits(frame, axis=1, bitorder='little').ravel()
        frame = mapping[frame].reshape(1080,1920)
        dir = file.parent / f'frame{i}.png'
        cv2.imwrite(str(dir), frame)
        del frame


def make_video(dir: Path, fps: int) -> Path: #codec: str = 'libx265', bitrate: int = 53453453 blahlbah options
    """
    Takes a directory Path as argument, where it will look for
    images with ordered naming scheme 'frame1.png', and create
    a .mp4 video from them.
    """
    ## TODO: replace with ffmpy wrapper lib
    output_path = dir / 'yb-output.mp4'
    cmd = (
        "ffmpeg -r {} -i {} -c:v libx264 -vf format=gray "
        "-crf 0 "
        # "-x265-params lossless=1 -tune grain " 
        "-y {}".format(
            fps, str(dir) + '/frame%d.png', 
            str(output_path))
        )
    subprocess.Popen(cmd, shell=True).wait()
    return output_path
    