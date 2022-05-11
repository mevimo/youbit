import cv2
import numpy as np
import ffmpeg
import time
import cProfile


pr = cProfile.Profile()
pr.enable()


bin = np.fromfile('C:/oldmonke.png', dtype=np.uint8)
bin = np.unpackbits(bin).reshape(-1,1)
print('SIZE: ' + str(bin.size) + ' !!!!!!!!!!!!!!!!!!!!')
zeros = np.zeros(1165496, dtype=np.uint8)
bin = np.append(bin, zeros)

bin[bin != 0] = 255

frame_count = int(bin.size / 2073600)
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



container = av.open("C:/OUTPUT.mp4", mode="w")

stream = container.add_stream("libx264", rate=1)
stream.width = 1920
stream.height = 1080
stream.pix_fmt = "gray"

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




pr.print_stats(sort='tottime')
pr.disable()





# cap = cv2.VideoCapture('C:/OUTPUT.mp4')

# index = 0

# while(cap.isOpened()):
#     ret, frame = cap.read()
#     if index == 0:
#         print(frame)
#     index += 1