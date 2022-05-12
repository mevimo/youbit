import cv2
import numpy as np
import ffmpeg
import time
import cProfile
import subprocess
import imageio


pr = cProfile.Profile()
pr.enable()

framesize = 2073600

bin = np.fromfile('E:/biggie.mp4.mp4', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1) #1bpp
zeros = np.zeros(framesize - (bin.size % framesize), dtype=np.uint8)
bin = np.append(bin, zeros)

bin[bin != 0] = 255
# bin = bin[:2073600]
# bin = np.split(bin, 50)

frame_count = int(bin.size / framesize)
bin = bin.reshape((frame_count, 1920, 1080))
# bin = np.split(bin, frame_count)
# print(bin)
# print(bin.shape)

# process = (
#     ffmpeg
#         .input('pipe:', format='rawvideo', pix_fmt='gray', s='1920x1080', r=1)
#         .output('OUTPUT.mp4', pix_fmt='gray', vcodec='libx265', r=1)
#         .extra_args('-x265-params', 'lossless=1')
#         .overwrite_output()
#         .run_async(pipe_stdin=True)
# )
# process.stdin.write(bin)
# process.stdin.close()
# process.wait()








import av



container = av.open("E:/AV_OUTPUT.mp4", mode="w")

stream = container.add_stream("libx264", rate=1)
stream.width = 1920
stream.height = 1080
stream.pix_fmt = "gray"
stream.options = {'crf': '0'}

for framebin in bin:
    frame = av.VideoFrame.from_ndarray(framebin, format="gray")
    # container.mux(stream.encode())
    for packet in stream.encode(frame):
        container.mux(packet)

# Flush stream
for packet in stream.encode():
    container.mux(packet)
# container.mux(stream.encode())

# Close the file
container.close()




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



pr.print_stats(sort='tottime')
pr.disable()





# cap = cv2.VideoCapture('C:/OUTPUT.mp4')

# index = 0

# while(cap.isOpened()):
#     ret, frame = cap.read()
#     if index == 0:
#         print(frame)
#     index += 1