from youbit import util
import os
import numpy as np
from pathlib import Path
import gzip
import youbit.ecc
import shutil

fileone = 'E:/test3.jpg'
filetwo = 'E:/oh/test3.jpg'

from youbit.video import VideoDecoder


for i in VideoDecoder('E:/yb-output.mp4'):
    pass

print('ok')

# y = youbit.ecc.ecc_encode(x)
# print(y)
# z = youbit.ecc.ecc_decode(x, 32)
# print(len(z))

# x = bytearray([1,2,3,4,5,6,7,8,9,10,11,22,33,44,55,66,77,88,99])  # length of 19 (19+32=51)
# x.extend([0,0]*102)
# y = youbit.ecc.ecc_encode(x)

# print(y)
# print(len(y))

# print(youbit.ecc.ecc_decode(y, 32))

# zeros = bytearray([0,0,0,0,0,0,0,0,0,0]*100)  #1000
# y.extend(zeros)

# print(len(y))

# print(youbit.ecc.ecc_decode(y, 32))



# with open('E:/test2.jpg', "rb") as f_in, gzip.open('E:/test2.gz', "wb") as f_out:
#     shutil.copyfileobj(f_in, f_out)



# with gzip.open('E:/test2.gz', "rb") as f_in, open('E:/oh/qick/test2.jpg', "wb") as f_out:
#     shutil.copyfileobj(f_in, f_out)






# arr = b'sdfqsdfqfqsdfqsdfqsdfq'
# print(len(arr))
# gzip.compress(arr)
# print(len(arr))

# with open('E:/test3.jpg', "rb") as f_in, open('E:/oh/test3.jpg', 'wb') as f_out:
#     while True:
#         arr = f_in.read(6500)
#         if not arr:
#             break
#         # print(len(arr))
#         arr = gzip.compress(arr)
#         # print(len(arr))
#         arr = gzip.decompress(arr)
#         f_out.write(arr)

# with open('E:/oh/test3.gz', 'wb') as f:
#     f.write(gzip.decompress(arr))

# report = util.compare_files(fileone, filetwo)

# print(report)



# print(os.path.getsize(fileone))
# print(os.path.getsize(filetwo))

# arr = np.fromfile(fileone, dtype=np.uint8)

# print(arr.size)



# arr1, arr2 = util.load_ndarray(Path(fileone)), util.load_ndarray(Path(filetwo))
# size_difference = abs(arr1.size - arr2.size)
# zeros = np.zeros(size_difference, dtype=np.uint8)
# if arr1.size < arr2.size:
#     arr1 = np.append(arr1, zeros)
#     arr1.tofile(str(fileone))
# elif arr2.size < arr1.size:
#     arr2 = np.append(arr2, zeros)
#     arr2.tofile(str(filetwo))
# assert arr1.size == arr2.size
