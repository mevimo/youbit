from numba import njit, prange, jit
from numba.typed import List
import numpy as np
from time import time
import av
from youbit import decode, encode
from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError, DownloadError
from youbit import util
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import cv2

import re

from youbit import Encoder, Decoder
from youbit.video import VideoDecoder
from youbit import util
from youbit.download import Downloader




x = Downloader('https://youtu.be/6IbYKM0ukrc')
x.download('E:/testy/', 'E:/testy/')



# def print_formats(info: dict):
#     for k,v in info.items():
#         if k == 'formats':
#             for i in v:
#                 if i['height'] == 1080:
#                     print('format id: ' + i.get('format_id'))
#                     print('vbr: ' + str(i.get('vbr')))
#                     print('quality: ' + str(i.get('quality')))
#                     print('resolution: ' + i.get('resolution'))
#                     print('video extension: ' + i.get('video_ext'))
#                     print('audio extension: ' + i.get('audio_ext'))
#                     print('fps: ' + str(i.get('fps')))
#                     print()




# x = Downloader('https://www.youtube.com/watch?v=LkwiwEy2mvg')
# # print_formats(x.info)
# print(x.info['id'])
# print(x.info['title'])
# print(x.info['description'])
# for k,v in x.info.items():
#     print(k,v)




# Encoder('E:/test2.jpg').encode('E:/INPUTFORYT.mp4', bpp=1, overwrite=True)

# Decoder('E:/test2bpp1.mkv').decode('E:/test2bpp1.jpg', bpp=1, overwrite=True)


# result = util.compare_files(
#     'E:/test2bpp1.jpg',
#     'E:/test2.jpg'
# )
# for k,v in result.items():
#     print(k, v)
#     print()




# for frame in VideoDecoder(Path('E:/dev/youbit/test2.jpg.mkv')):
#     pass

# frames= []

# for frame in VideoDecoder(Path('E:/dev/youbit/test2.jpg.mkv')):
#     frame = decode.read_pixels(frame, 2)
#     frames.append(frame)
# output_arr = np.concatenate(frames, dtype=np.uint8)
# output_arr.tofile(Path('E:/testok.jpg'))




URL = 'https://youtu.be/9QX5b1vtfLA'
# # opts = {
# #     'cookiesfrombrowser': ('chrome', ),
# #     'cookiefile': 'cookies'
# # }

# opts = {
#     'logtostderr': True,
# }

# x = open(os.devnull, 'w')

# with redirect_stderr(x): # yt-dlp will print the error message to stderr in addition to raising an exception, effectively writing dublicate information to terminal. There are no flags that alter this behavior.
#     with YoutubeDL(opts) as ydl:
#         try:
#             info = ydl.extract_info(URL, download=False)
#         except DownloadError as e:
#             raise ValueError(f'Passed url is invalid: {e}')
#         ydl.download([URL])





# opts = {
#     'logtostderr': True,
#     # 'format': format_selector,
#     # 'format_sort': ['vext', 'vbr']
# }
# x = open(os.devnull, 'w')
# with redirect_stderr(x):
#     with YoutubeDL(opts) as ydl:
#         info = ydl.extract_info(URL, download=False)
#         # ydl.download([URL])


# # print(info['vbr'])


# for k,v in info.items():
#     if k == 'formats':
#         print(v[-1])

#         for i in v:
#             if i['height'] == 1080:
#                 print('format id: ' + i.get('format_id'))
#                 print('vbr: ' + str(i.get('vbr')))
#                 print('quality: ' + str(i.get('quality')))
#                 print('resolution: ' + i.get('resolution'))
#                 print('video extension: ' + i.get('video_ext'))
#                 print('audio extension: ' + i.get('audio_ext'))
#                 print('fps: ' + str(i.get('fps')))

#                 print()
    
#             # print(i)
        
#         print('correct res:::::::::::::::')
#         correct_res = [i for i in v if i['resolution'] == '1920x1080']
#         correct_res.sort(reverse=True, key = lambda x : x['vbr'])
#         print(correct_res[0])
#         # print(v)









# bpp = None

# with Encoder(Path('E:/test2.jpg')) as encoder:
#     encoder.encode('E:/INPUTFORYT.mp4', overwrite=True, bpp=2)
#     bpp = encoder.metadata['bpp']

# with Decoder(Path('E:/dev/youbit/test2.jpg.mkv')) as decoder:
#     decoder.decode('E:/testoutputty2.jpg', bpp=2, overwrite=True)



# cap = cv2.VideoCapture('E:/testoutputty.mp4')

# while(cap.isOpened()):
#     ret, frame = cap.read()
#     x = frame.flatten()[:1500]
#     x = np.delete(x, np.arange(0, x.size, 3))
#     x = np.delete(x, np.arange(0, x.size, 2))
#     print(x)
#     break








# re_string = "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"

# stringy = 'E:/google.com'

# print(re.search(re_string, stringy))


















# arr = [i for i in range(256)] * 8100
# arr = np.array(arr, dtype=np.uint8)

# print(arr[:50])

# arr = decode.read_pixels(arr, 2)

# print(arr[:50])
# print(arr.size)
# print(arr[-50:])

# np.save('test_read_pixels_solution_bpp2.npy', arr)









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


# from youbit._video_code import VideoDecoder
# from youbit.decode import read_pixels
# from pathlib import Path
# import time


# path = Path('E:/output.mp4')
# with VideoDecoder(path) as video:
#     frame = video.get_frame()
#     print(frame[:50])
#     tik = time.time()
#     frame = read_pixels(frame, 1)
#     tok = time.time()
#     print('frame time: ' + str(tok-tik))
#     print(frame[:50])

# #     print('------------------------------')
# #     tik = time.time()
# #     frame = read_pixels(frame, 3)
# #     tok = time.time()
# #     print(frame[:50])

# #     print('total time: ' + str(tok-tik))

# tikk = time.time()

# arr = np.array([], dtype=np.uint8)

# tottime = 0

# # for _ in range(100):
# #     for frame in VideoDecoder(path):
# #         tik = time.time()
# #         read_pixels(frame, 3)
# #         tottime += (time.time() - tik)




# tokk = time.time()

# print('total: ' + str(tokk-tikk))
# print('time spent reading pixels: ' + str(tottime))


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