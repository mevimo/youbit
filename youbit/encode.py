from ast import Raise
import cv2
import subprocess
import numpy as np
from pathlib import Path
from par2deep.par2deep import par2deep


def apply_ecc(tempdir: Path, pc: int) -> None:
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
    ## TODO: switch to par2.exe control via subprocess, package youbit with binaries for linux and windows
    par = par2deep(str(tempdir))
    par.args['quiet'] = True
    par.args['percentage'] = pc
    par.args['clean_backup'] = True
    par.check_state()
    for _ in par.execute(): pass


def make_frames(tempdir: Path, bpp: int) -> tuple:
    ## TODO: chunking, reading each file out in chunks, big loop, create 1 frame each loop. Multithrading
    ## NOTE: Mumtithreading?
    # Right now this uses an insane amount of ram, roughly equal to the filesize,
    # since it is completely saved in memory as a contiguous numpy array.
    for file in tempdir.iterdir():
        if 'vol' in file.name and file.suffix == '.par2':
            par_recovery = np.fromfile(str(file), dtype=np.uint8)
            file.unlink()
        elif file.suffix == '.par2':
            par_parity = np.fromfile(str(file), dtype=np.uint8)
            file.unlink()
        else:
            par_main = np.fromfile(str(file), dtype=np.uint8)
            file.unlink()
    par_parity_size = par_parity.size   
    par_recovery_size = par_recovery.size
    bin = np.concatenate((par_parity, par_recovery, par_main))
    del par_parity, par_recovery, par_main

    # NOTE: Trailing zero bytes on a gzip does not affect checksum of underlying file
    framesize = 259200 * bpp
    filler_bytes = framesize - (bin.size // framesize)
    if filler_bytes != 0:
        zeros = np.zeros(filler_bytes, dtype=np.uint8)
        bin = np.append(bin, zeros)
        del zeros
    framecount = bin.size // framesize

    if bpp == 1:
        for i in range(framecount):
            start = framesize * i
            stop = start + framesize
            frame = np.unpackbits(bin[start:stop])
            frame[frame != 0] = 255
            dir = tempdir / f'frame{i}.png'
            cv2.imwrite(str(dir), frame.reshape(1080,1920))
            del frame
    elif bpp == 2 or bpp == 3:
        mapping = np.array([0,144,80,208,48,176,112,255]) # not tested if this mapping also works with a bpp of 2
        for i in range(framecount):
            start = framesize
            stop = start + framesize
            frame = np.unpackbits(bin[start:stop]).reshape(-1,bpp)
            frame = np.packbits(frame, axis=1, bitorder='little').ravel()
            frame = mapping[frame].reshape(1080,1920)
            dir = tempdir / f'frame{i}.png'
            cv2.imwrite(str(dir), frame)
            del frame
    else:
        raise ValueError('Unsupported BPP (Bits Per Pixel) value.')
    return par_parity_size, par_recovery_size

 
def make_video(tempdir: Path, fps: int = 1) -> Path: # losless or not option
    """
    Given a directory, all ordered images with syntax 'frame1.png' will be used to assemble a video.
    """
    ## TODO: replace with ffmpy wrapper lib low priority
    output_path = tempdir / 'yb-output.mp4'
    cmd = (
        "ffmpeg -r {} -i {} -c:v libx265 -vf format=gray "
        "-x265-params lossless=1 -tune grain " 
        "-y {}".format(
            fps, str(tempdir) + '/frame%d.png', 
            str(output_path))
        )
    subprocess.Popen(cmd, shell=True).wait()
    return output_path
    