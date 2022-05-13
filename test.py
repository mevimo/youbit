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

bin = np.fromfile('C:/oldmonke.png', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1) #1bpp
zeros = np.zeros(framesize - (bin.size % framesize), dtype=np.uint8)
bin = np.append(bin, zeros)

bin[bin != 0] = 255
# bin = bin[:2073600]
# bin = np.split(bin, 50)

frame_count = int(bin.size / framesize)
bin = bin.reshape((frame_count, 1080, 1920))
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

pr.print_stats(sort='tottime')
pr.disable()


print(bin.flatten()[:500])
print('---------------------------------------------')






import av



container = av.open("C:/AV_OUTPUT.mp4", mode="w")

stream = container.add_stream("libx264", rate=1)
stream.width = 1920
stream.height = 1080
stream.options = {'crf':'0'}
# stream.options = {'crf': '20', 'tune': 'grain', '-x264opts': 'no-deblock'}

for framebin in bin:
    frame = av.VideoFrame.from_ndarray(framebin, format="gray")
    # stream.encode(frame)

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








cap = cv2.VideoCapture('C:/AV_OUTPUT.mp4')


while(cap.isOpened()):
    ret, frame = cap.read()
    x = frame.flatten()[:1500]
    x = np.delete(x, np.arange(0, x.size, 3))
    x = np.delete(x, np.arange(0, x.size, 2))
    print(x)
    break