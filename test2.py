from youbit import lowlevel_encode
from pathlib import Path
import cProfile
import numpy as np
import ffmpeg
import cv2

pr = cProfile.Profile()
pr.enable()

file = Path('E:/biggie.mp4')
lowlevel_encode.encode(file, Path('E:/yb-output.mp4'), 3)

# bin = np.fromfile('C:/oldmonke.png', dtype=np.uint8)
# bin = np.unpackbits(bin).reshape(-1,3) #1bpp
# bin[bin != 0] = 255
# print(bin.flatten()[:500])
# print('---------------------------------------------')





pr.print_stats(sort='tottime')
pr.disable()




cap = cv2.VideoCapture('E:/yb-output.mp4')


while(cap.isOpened()):
    ret, frame = cap.read()
    x = frame.flatten()[:1500]
    x = np.delete(x, np.arange(0, x.size, 3))
    x = np.delete(x, np.arange(0, x.size, 2))
    print(x)
    break