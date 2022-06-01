import cv2
import subprocess
import numpy as np
from numba import njit, prange
import time



# @njit('void(uint8[::1], uint8[::1], uint8[::1])', inline='never')
# def _numba_transform_bpp3_x64(arr, out, mapping):
#     for i in range(64):
#         j = i * 3
#         out[i] = mapping[(arr[j]<<2)|(arr[j+1]<<1)|(arr[j+2])]


# @njit('void(uint8[::1], uint8[::1])')
# def _numba_read_bpp3(arr, out):
#     for i in range(arr.size):
#         if arr[i] < 32:
#             out[i] = 0
#         if 32 <= arr[i] < 64:
#             out[i] = 1
#         if 64 <= arr[i] < 96:
#             out[i] = 2
#         if 96 <= arr[i] < 128:
#             out[i] = 3
#         if 128 <= arr[i] < 160:
#             out[i] = 4
#         if 160 <= arr[i] < 192:
#             out[i] = 5
#         if 192 <= arr[i] < 224:
#             out[i] = 6
#         if 224 <= arr[i]:
#             out[i] = 7


# @njit('void(uint8[::1], uint8[::1])')
# def _numba_read_bpp3(arr, out):
#     for i in range(arr.size):
#         j = i * 3
#         if arr[i] < 32:
#             out[j] = 0
#             out[j+1] = 0
#             out[j+2] = 0
#         if 32 <= arr[i] < 64:
#             out[j] = 0
#             out[j+1] = 0
#             out[j+2] = 1
#         if 64 <= arr[i] < 96:
#             out[j] = 0
#             out[j+1] = 1
#             out[j+2] = 0
#         if 96 <= arr[i] < 128:
#             out[j] = 0
#             out[j+1] = 1
#             out[j+2] = 1
#         if 128 <= arr[i] < 160:
#             out[j] = 1
#             out[j+1] = 0
#             out[j+2] = 0
#         if 160 <= arr[i] < 192:
#             out[j] = 1
#             out[j+1] = 0
#             out[j+2] = 1
#         if 192 <= arr[i] < 224:
#             out[j] = 1
#             out[j+1] = 1
#             out[j+2] = 0
#         if 224 <= arr[i]:
#             out[j] = 1
#             out[j+1] = 1
#             out[j+2] = 1

# @njit('void(uint8[::1], uint8[::1], uint8[::1])', inline='never')
# def _numba_transform_bpp3_x64(arr, out, mapping):
#     for i in range(64):
#         j = i * 3
#         out[i] = mapping[(arr[j]<<2)|(arr[j+1]<<1)|(arr[j+2])]


# @njit('void(uint8[::1], int_, uint8[::1], uint8[::1])', parallel=True)
# def _numba_transform_bpp3(arr, div, out, mapping):
#     for i in prange(div//64):
#         _numba_transform_bpp3_x64(arr[i*192:(i*192)+192], out[i*64:(i*64)+64], mapping)


@njit('void(uint8[::1], uint8[::1])', inline='never')
def _numba_pack_x64(arr, out):
    for i in range(64):
        j = i * 8
        out[i] = (arr[j]<<7)|(arr[j+1]<<6)|(arr[j+2]<<5)|(arr[j+3]<<4)|(arr[j+4]<<3)|(arr[j+5]<<2)|(arr[j+6]<<1)|arr[j+7]

       
@njit('void(uint8[::1], uint8[::1])', parallel=True)
def _numba_pack(arr, out):
    for i in prange(out.size//64):
        _numba_pack_x64(arr[i*512:(i*512)+512], out[i*64:(i*64)+64])
    # for i in range(div//64*64, div):
    #     j = i * 8
    #     su[i] = (arr[j]<<7)|(arr[j+1]<<6)|(arr[j+2]<<5)|(arr[j+3]<<4)|(arr[j+4]<<3)|(arr[j+5]<<2)|(arr[j+6]<<1)|arr[j+7]
    

# @njit('void(uint8[::1], uint8[::1], bool_[::1])', inline='never')
# def _numba_read_bpp3_x64(arr, out, mapping):
#     for i in range(64):
#         j = i * 3
#         idx = (arr[i] * 3) >> 5
#         out[j] = mapping[idx]
#         out[j+1] = mapping[idx+1]
#         out[j+2] = mapping[idx+2]


# @njit('void(uint8[::1], uint8[::1])', parallel=True)
# def _numba_read_bpp2(arr, out):
#     mapping = np.array([0,0, 0,1, 1,0, 1,1], dtype=np.bool_)
#     # mapping1 = np.array([0, 0, 1, 1], dtype=np.bool_)
#     # mapping2 = np.array([0, 1, 0, 1], dtype=np.bool_)
#     # for i in prange(arr.size):
#     #     j = i * 2
#     #     idx = arr[i] >> 6
#     #     out[j] = mapping1[idx]
#     #     out[j+1] = mapping2[idx]
#     for i in prange(arr.size):
#         j = i * 2
#         idx = (arr[i] >> 6) * 2
#         out[j] = mapping[idx]
#         out[j+1] = mapping[idx+1]



# @njit('void(uint8[::1], uint8[::1])', inline='never')
# def _numba_read_bpp2_x128(arr, out):
#     for i in range(128):
#         j = i * 4
#         out[i] = (arr[j] & 192) | (arr[j+1] & 192 >> 2) | (arr[j+2] & 192 >> 4) | (arr[j+3] & 192 >> 6)



# @njit('void(uint8[::1], uint8[::1])', parallel=True)
# def _numba_read_bpp2(arr, out):
#     for i in prange(out.size):
#         idxarr = i*512
#         idxout = i*128
#         _numba_read_bpp2_x128(arr[idxarr:idxarr+512], out[idxout:idxout+128])


@njit('void(uint8[::1], uint8[::1])')
def _numba_read_bpp2(arr, out):
    #! cant get this to scale meaningfully with parallelism... is far from the bottleneck either way
    for i in range(out.size):
        j = i * 4
        out[i] = (arr[j] & 192) | (arr[j+1] & 192 >> 2) | (arr[j+2] & 192 >> 4) | (arr[j+3] & 192 >> 6)
    

# @njit('void(uint8[::1], uint8[::1])', parallel=True)
# def _numba_read_bpp3(arr, out):
#     mapping = np.array([0,0,0, 0,0,1, 0,1,0, 0,1,1, 1,0,0, 1,0,1, 1,1,0, 1,1,1], dtype=np.bool_)
#     # for i in prange(arr.size // 64):
#     #     _numba_read_bpp3_x64(arr[i*64:(i*64)+64], out[i*192:(i*192)+192], mapping)
#     for i in prange(arr.size):
#         j = i * 3
#         idx = (arr[i] >> 5) * 3
#         out[j] = mapping[idx]
#         out[j+1] = mapping[idx+1]
#         out[j+2] = mapping[idx+2]
    

@njit('void(uint8[::1], uint8[::1])')
def _numba_read_bpp3(arr, out):
    for i in range(out.size//3):
        arr_i = i * 8
        out_x3 = ((arr[arr_i] & 224) << 16) | ((arr[arr_i+1] & 224) << 13) | ((arr[arr_i+2] & 224) << 10) | ((arr[arr_i+3] & 224) << 7) | ((arr[arr_i+4] & 224) << 4) | ((arr[arr_i+5] & 224) << 1) | ((arr[arr_i+6] & 224) >> 2) | ((arr[arr_i+7] & 224) >> 5)
        out_i = i * 3
        out[out_i] = out_x3 >> 16 & 255 # technically not necesarry might remove bitwise AND
        out[out_i+1] = out_x3 >> 8 & 255
        out[out_i+2] = out_x3 & 255


@njit('void(uint8[::1])')
def _numba_read_bpp1(arr):
    for i in range(len(arr)):
        arr[i] = arr[i] >> 7


def read_pixels(arr: np.ndarray, bpp: int) -> np.ndarray:
    """Expects a numpy ndarray of datatype uint8.
    Each element is expected to represent an entire pixel.
    (gray pixel format)."""
    if bpp == 1:
        _numba_read_bpp1(arr)
        out = np.packbits(arr)
    elif bpp == 2:
        # out = np.zeros(arr.size*2, dtype=np.uint8)
        # _numba_read_bpp2(arr, out)
        # out = np.packbits(out)
        out = np.zeros(arr.size//4, dtype=np.uint8)
        _numba_read_bpp2(arr, out)
    elif bpp == 3:
        # out = np.zeros(arr.size*3, dtype=np.uint8)
        # _numba_read_bpp3(arr, out)
        # out = np.packbits(out)
        out_size = int(arr.size * 3 / 8)
        out = np.zeros(out_size, dtype=np.uint8)
        _numba_read_bpp3(arr, out)
    return out













def extract_frames(tempdir) -> None:
    file = tempdir.glob('*.mp4').send(None)
    cmd = "ffmpeg -i {} -r 1/1 {}/frame%d.png".format( # 1 frame captures per second, which leave 2 unusable frame in beginning for unknown reasons
        str(file), str(tempdir))
    subprocess.Popen(cmd, shell=True).wait()
    # Remove video file
    file.unlink()


def extract_binary(tempdir, par_parity_size: int, par_recovery_size: int, bpp: int) -> None:
    '''assumes frameé".png naming blahblha'''
    ## TODO: extract key frames only for much less error rate, but I have to figure out YouTube's GOP structure first
    # 12th frame is keyframe duplicate, as well as 29th frame and 46th frame... distance of 17 frames with first dupe-key-frame at 12?
    # my 1fps is being transformed into a higher fps, maybe thats why?
    # might be a coincidental correlation....
    frame_paths = sorted(
        tempdir.glob('*.png'),
        key = lambda p : int(p.stem[5:])
        # key=os.path.getmtime
        )
    frames = []

    if bpp == 1:
        for f in frame_paths:
            if f.name in ('frame1.png', 'frame2.png'): ## code duplication, remove  from frames var before this code block
                continue
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            pixels = np.array(img, dtype=np.uint8)
            del img
            pixels[pixels < 128] = 0
            pixels[pixels > 127] = 1
            frames.append(np.packbits(pixels))
            del pixels
    elif bpp == 2:
        ##TODO
        pass
    elif bpp == 3:
        for f in frame_paths:
            if f.name in ('frame1.png', 'frame2.png'):
                continue
            pixels = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            pixels[pixels < 32] = 0 #000
            pixels[(pixels >= 32) & (pixels < 64)] = 1 #001
            pixels[(pixels >= 64) & (pixels < 96)] = 2 #010
            pixels[(pixels >= 96) & (pixels < 128)] = 3 #011
            pixels[(pixels >= 128) & (pixels < 160)] = 4 #100
            pixels[(pixels >= 160) & (pixels < 192)] = 5 #101
            pixels[(pixels >= 192) & (pixels < 224)] = 6 #110
            pixels[pixels >= 224] = 7 #111
            pixels = np.unpackbits(pixels).reshape(-1,8)
            pixels = np.delete(pixels, [0,1,2,3,4], 1).ravel()
            frames.append(np.packbits(pixels))
            del pixels
    
    bin = np.concatenate(frames)
    del frames

    par_parity_path = tempdir / 'bin.par2'
    bin[:par_parity_size].tofile(par_parity_path)
    par_recovery_path = tempdir / 'bin.vol0+0.par2'
    bin[par_parity_size:par_recovery_size].tofile(par_recovery_path)
    par_main_path = tempdir / 'bin'
    bin[par_recovery_size:].tofile(par_main_path)
    del bin


# def remove_ecc(tempdir):
#     ##TODO: switch to par2.exe binary 
#     subprocess.Popen(f'par2deep-cli -q -clean -dir {str(tempdir)}', shell=True).wait() #wont work because working directory of subprocess is not yet set to the youbit/youbit

#     for file in tempdir.glob('*.par2'):
#         file.unlink()

