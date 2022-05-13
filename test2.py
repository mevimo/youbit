from youbit import lowlevel_encode
from pathlib import Path
import cProfile
import numpy as np
import ffmpeg
import cv2

pr = cProfile.Profile()
pr.enable()

file = Path('C:/oldmonke.png')
lowlevel_encode.make_frames(file, 1)
lowlevel_encode.make_video(file.parent, 1)

bin = np.fromfile('C:/oldmonke.png', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1) #1bpp
bin[bin != 0] = 255
print(bin.flatten()[:500])
print('---------------------------------------------')


# framesize = 2073600

# bin = np.fromfile('C:/oldmonke.png', dtype=np.uint8)
# bin = np.unpackbits(bin).reshape(-1,1) #1bpp
# zeros = np.zeros(framesize - (bin.size % framesize), dtype=np.uint8)
# bin = np.append(bin, zeros)

# bin[bin != 0] = 255

# process = (
#     ffmpeg
#         .input('pipe:', format='rawvideo', pix_fmt='gray', s='1920x1080', r=1)
#         .output('OUTPUT.mp4', pix_fmt='gray', vcodec='libx264', crf=0, r=1)
#         .overwrite_output()
#         .run_async(pipe_stdin=True)
# )
# process.stdin.write(bin)
# process.stdin.close()
# process.wait()




pr.print_stats(sort='tottime')
pr.disable()




cap = cv2.VideoCapture('C:/yb-output.mp4')


while(cap.isOpened()):
    ret, frame = cap.read()
    x = frame.flatten()[:1500]
    x = np.delete(x, np.arange(0, x.size, 3))
    x = np.delete(x, np.arange(0, x.size, 2))
    print(x)
    break