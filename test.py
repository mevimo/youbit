import cv2
import numpy as np
import ffmpeg
import time
import cProfile
import subprocess
import imageio


pr = cProfile.Profile()
pr.enable()


bin = np.fromfile('E:/newtestyb/test2.jpg', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1)
zeros = np.zeros(30176, dtype=np.uint8)
bin = np.append(bin, zeros)


bin[bin != 0] = 255
# bin = bin[:2073600]
# bin = np.split(bin, 50)


imageio.mimwrite(
    'outputty.mp4',
    [b.reshape(1080,1920) for b in np.split(bin, 50)],
    fps=1
)



# process = (
#     ffmpeg
#         .input('pipe:', format='rawvideo', pix_fmt='gray', s='1920x1080', r=1)
#         .output('OUTPUT.mp4', pix_fmt='gray', vcodec='libx265', r=1)
#         .global_args('-x265-params', 'lossless=1')
#         .overwrite_output()
#         # .run_async(pipe_stdin=True)
# )

# args = process.get_args()
# process = process.run_async(pipe_stdin=True)
# print(f'Args: {args}')

# process.stdin.write(bin)
# process.stdin.close()
# process.wait()



# process = subprocess.Popen([
#     'ffmpeg',
#     '-f', 'rawvideo',
#     'pix_fmt', 'gray',
#     '-r', '1',
#     '-s', '1920x1080',
#     '-i', 'pipe:',
#     '-pix_fmt', 'gray',
#     '-r', '1',
#     '-vcodec', 'libx265',
#     # '-x265-params', 'lossless=1',
#     'outputty.mp4', 'y'
# ], stdin=subprocess.PIPE)


# # # process.communicate(bin.tobytes())
# process.stdin.write(bin.tobytes())
# process.stdin.close()
# process.wait()



# pr.print_stats(sort='tottime')
pr.disable()


# cap = cv2.VideoCapture('OUTPUT.mp4')

# index = 0

# while(cap.isOpened()):
#     ret, frame = cap.read()
#     if index == 0:
#         print(frame)
#     index += 1