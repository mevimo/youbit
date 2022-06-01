from numba import njit, prange, jit
from numba.typed import List
import numpy as np
from time import time
import av



# bin = np.random.randint(2, size=100000002, dtype=bool)
# print(bin[:8])

# @njit('void(bool_[::1], uint8[::1], int_)', inline='never')
# def _numba_pack_x64(arr, su, pos):
#     for i in range(64):
#         j = i * 8
#         su[i] = (arr[j]<<7)|(arr[j+1]<<6)|(arr[j+2]<<5)|(arr[j+3]<<4)|(arr[j+4]<<3)|(arr[j+5]<<2)|(arr[j+6]<<1)|arr[j+7]
       
# @njit('void(bool_[::1], int_, uint8[::1])', parallel=True)
# def _numba_pack(arr, div, su):
#     for i in prange(div//64):
#         _numba_pack_x64(arr[i*8:(i+64)*8], su[i:i+64], i)
#         # print(i*8, (i+64)*8)
#     for i in range(div//64*64, div):
#         j = i * 8
#         su[i] = (arr[j]<<7)|(arr[j+1]<<6)|(arr[j+2]<<5)|(arr[j+3]<<4)|(arr[j+4]<<3)|(arr[j+5]<<2)|(arr[j+6]<<1)|arr[j+7]
        
# def numba_packbits(arr):
#     div, mod = np.divmod(arr.size, 8)
#     su = np.zeros(div + (mod>0), dtype=np.uint8)
#     _numba_pack(arr[:div*8], div, su)
#     if mod > 0:
#         su[-1] = sum(x*y for x,y in zip(arr[div*8:], (128, 64, 32, 16, 8, 4, 2, 1)))
#     return su

# tik = time()
# bin = numba_packbits(bin)
# tok = time()

# print(tok-tik)
# print(bin)


from youbit._video_code import VideoDecoder
from youbit._decode import read_pixels
from pathlib import Path
import time


path = Path('E:/output.mp4')
with VideoDecoder(path) as video:
    frame = video.get_frame()
    print(frame[:50])
    tik = time.time()
    frame = read_pixels(frame, 1)
    tok = time.time()
    print('frame time: ' + str(tok-tik))
    print(frame[:50])

#     print('------------------------------')
#     tik = time.time()
#     frame = read_pixels(frame, 3)
#     tok = time.time()
#     print(frame[:50])

#     print('total time: ' + str(tok-tik))

tikk = time.time()

arr = np.array([], dtype=np.uint8)

tottime = 0

# for _ in range(100):
#     for frame in VideoDecoder(path):
#         tik = time.time()
#         read_pixels(frame, 3)
#         tottime += (time.time() - tik)




tokk = time.time()

print('total: ' + str(tokk-tikk))
print('time spent reading pixels: ' + str(tottime))


# tik = time.time()

# print(arr.size)
# arr = read_pixels(arr, 3)

# tok = time.time()

# print('total time readpixel: ' + str(tok-tik))




# bon[bon < 32] = 0 #000
# bon[(bon >= 32) & (bon < 64)] = 1 #001
# bon[(bon >= 64) & (bon < 96)] = 2 #010
# bon[(bon >= 96) & (bon < 128)] = 3 #011
# bon[(bon >= 128) & (bon < 160)] = 4 #100
# bon[(bon >= 160) & (bon < 192)] = 5 #101
# bon[(bon >= 192) & (bon < 224)] = 6 #110
# bon[bon >= 224] = 7 #111
# bon = np.unpackbits(bon).reshape(-1,8)
# bon = np.delete(bon, [0,1,2,3,4], 1).ravel()
# bon = np.packbits(bon)


# print('-------------------')
# print(bin)
# print(bon)

# print(bin.shape, bon.shape)
# print(np.array_equal(bin,bon))

# print('-------------------------------')


# tik = time()
# bon = np.packbits(np.unpackbits(bin).reshape(-1,3), axis=1, bitorder='little')
# tok = time()


# print('numpy: ', bon.ravel()[:20])
# print('time: ', tok-tik)


# print('----------------------------------------------------')

# cap = cv2.VideoCapture('E:/yt-output.mp4')


# while(cap.isOpened()):
#     ret, frame = cap.read()
#     x = frame.flatten()[:1500]
#     x = np.delete(x, np.arange(0, x.size, 3))
#     x = np.delete(x, np.arange(0, x.size, 2))
#     print(x)
#     break