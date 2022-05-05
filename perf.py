from youbit import lowlevel_encode
from pathlib import Path
import time

tik = time.time()

file = Path('E:/newtestyb/test2.jpg')
lowlevel_encode.make_frames(file, 1)

tok = time.time()
print(tok-tik)
