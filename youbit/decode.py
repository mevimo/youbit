import os
import cv2
import subprocess
import numpy as np
from pathlib import Path
from par2deep.par2deep import par2deep

##TODO: Chunking, just like in encode.py

def extract_frames(tempdir) -> None:
    file = tempdir.glob('*.mp4').send(None)
    cmd = "ffmpeg -i {} -r 1/1 {}/frame%d.png".format( # 1 frame captures per second, which leave 2 unusable frame in beginning for unknown reasons
        str(file), str(tempdir))
    subprocess.Popen(cmd, shell=True).wait()
    # Remove video file
    file.unlink()


def extract_binary(tempdir, par_parity_size: int, par_recovery_size: int, bpp: int) -> None:
    ## TODO: extract key frames only for much less error rate, but I have to figure out YouTube's GOP structure first
    # 12th frame is keyframe duplicate, as well as 29th frame and 46th frame... distance of 17 frames with first dupe-key-frame at 12?
    # might be a coincidental correlation....
    frame_paths = sorted(
        tempdir.glob('*.png'),
        key=os.path.getmtime
        )
    frames = []

    if bpp == 1:
        for f in frame_paths:
            if f.name in ('frame1.png', 'frame2.png'):
                continue
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            pixels = np.array(img, dtype=np.uint8)
            del img
            pixels[pixels < 128] = 0
            pixels[pixels > 127] = 1
            frames.append(np.packbits(pixels))
            del pixels
    elif bpp == 2:
        ##TODO
        pass
    elif bpp == 3:
        for f in frame_paths:
            if f.name in ('frame1.png', 'frame2.png'):
                continue
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            pixels = np.array(img, dtype=np.uint8)
            del img
            pixels[pixels < 32] = 0 #000
            pixels[(pixels >= 32) & (pixels < 64)] = 1 #001
            pixels[(pixels >= 64) & (pixels < 96)] = 2 #010
            pixels[(pixels >= 96) & (pixels < 128)] = 3 #011
            pixels[(pixels >= 128) & (pixels < 160)] = 4 #100
            pixels[(pixels >= 160) & (pixels < 192)] = 5 #101
            pixels[(pixels >= 192) & (pixels < 224)] = 6 #110
            pixels[pixels >= 224] = 7 #111
            pixels = np.unpackbits(pixels).reshape(-1,8)
            pixels = np.delete(pixels, [0,1,2,3,4], 1).ravel()
            frames.append(np.packbits(pixels))
            del pixels
    
    bin = np.concatenate(frames)
    del frames

    par_parity_path = tempdir / 'bin.par2'
    bin[:par_parity_size].tofile(par_parity_path)
    par_recovery_path = tempdir / 'bin.vol0+0.par2'
    bin[par_parity_size:par_recovery_size].tofile(par_recovery_path)
    par_main_path = tempdir / 'bin'
    bin[par_recovery_size:].tofile(par_main_path)
    del bin


def remove_ecc(tempdir):
    ##TODO: switch to par2.exe binary 
    subprocess.Popen(f'par2deep-cli -q -clean -dir {str(tempdir)}', shell=True).wait() #wont work becauseworking directory of subprocess is not yet set to the youbit/youbit

    for file in tempdir.glob('*.par2'):
        file.unlink()

