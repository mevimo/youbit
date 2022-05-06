import cv2
import numpy as np
import ffmpeg
import time
import cProfile


pr = cProfile.Profile()
pr.enable()


bin = np.fromfile('C:/monke.png', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1)
zeros = np.zeros(1165496, dtype=np.uint8)
bin = np.append(bin, zeros)


bin[bin != 0] = 255


print(bin)

process = (
    ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='gray', s='1920x1080', r=1)
        .output('OUTPUT.mp4', pix_fmt='gray', vcodec='libx265', r=1)
        .extra_args('-x265-params', 'lossless=1')
        .overwrite_output()
        .run_async(pipe_stdin=True)
)
process.stdin.write(bin)
process.stdin.close()
process.wait()


pr.print_stats(sort='tottime')
pr.disable()


cap = cv2.VideoCapture('OUTPUT.mp4')

index = 0

while(cap.isOpened()):
    ret, frame = cap.read()
    if index == 0:
        print(frame)
    index += 1