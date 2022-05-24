from numba import njit, prange, jit
from numba.typed import List
import numpy as np
from time import time



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


print('---------------------------------')
bin = np.random.randint(256, size=20736, dtype=np.uint8)
# bin = np.random.randint(2, size=207360000, dtype=np.uint8)
print('bin: ', bin[:20])
# bin = np.unpackbits(bin)
print('----------------------------')



@njit('void(uint8[::1], uint8[::1], uint8[::1])', inline='never')
def _numba_pack_x64(arr, su, mapping):
    uarr = np.zeros(192, dtype=np.uint8)
    for i in range(24):
        for n in range(7, -1, -1):
            k = arr[i] >> n
            uarr[i*8+(7-n)] = (k & 1)
    # for i in range(192):
    #     k = arr[i//8] >> (7 - (i % 8))
    #     uarr[i] = (k & 1)
    for i in range(64):
        j = i * 3
        su[i] = mapping[(uarr[j]<<2)|(uarr[j+1]<<1)|(uarr[j+2])]
       
@njit('void(uint8[::1], int_, uint8[::1], uint8[::1])', parallel=True)
def _numba_pack(arr, div, su, mapping):
    for i in prange(div//64):
        _numba_pack_x64(arr[i*24:(i*24)+24], su[i*64:(i*64)+64], mapping)
        
def transform_array(arr):
    div, mod = np.divmod(arr.size*8, 3)
    su = np.zeros(div + (mod>0), dtype=np.uint8)

    # mapping = np.array([0,144,80,208,48,176,112,255], dtype=np.uint8)
    mapping = np.array([0,48,80,112,144,176,208,255], dtype=np.uint8)

    _numba_pack(arr[:div*3], div, su, mapping)
    if mod > 0:
        print('THERES A MOD')
        su[-1] = sum(x*y for x,y in zip(arr[div*3:], (128, 64, 32, 16, 8, 4, 2, 1)))
    # return mapping[su]
    return su


tik = time()
# bin = np.unpackbits(bin)
bon = transform_array(bin)
tok = time()

print('numba: ', bon[:20])
print('time: ', tok-tik)


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