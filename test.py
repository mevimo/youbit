import cv2
import numpy as np
import ffmpeg
import time
import cProfile
import subprocess
import imageio




cap = cv2.VideoCapture('E:/yb-output.mp4')


while(cap.isOpened()):
    ret, frame = cap.read()
    x = frame.flatten()[:1500]
    x = np.delete(x, np.arange(0, x.size, 3))
    x = np.delete(x, np.arange(0, x.size, 2))
    print(x)
    break



print('----------------------------------------------------')

cap = cv2.VideoCapture('E:/yt-output.mp4')


while(cap.isOpened()):
    ret, frame = cap.read()
    x = frame.flatten()[:1500]
    x = np.delete(x, np.arange(0, x.size, 3))
    x = np.delete(x, np.arange(0, x.size, 2))
    print(x)
    break