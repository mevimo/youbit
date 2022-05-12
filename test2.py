from youbit import lowlevel_encode
from pathlib import Path
import cProfile

pr = cProfile.Profile()
pr.enable()

file = Path('C:/oldmonke.png')
lowlevel_encode.make_frames(file, 1)
lowlevel_encode.make_video(file.parent, 1)

pr.print_stats(sort='tottime')
pr.disable()