from youbit import util
import os
import numpy as np
from pathlib import Path
import gzip
import youbit.ecc

fileone = 'E:/test3.jpg'
filetwo = 'E:/oh/test3.jpg'

from youbit.video import VideoDecoder








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
