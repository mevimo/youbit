<p align="center">
<a href="https://github.com/MeViMo/youbit/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/pypi/l/youbit?color=99ddcc" alt="License">
</a>
<a href="https://pypi.org/project/youbit/" target="_blank">
    <img src="https://img.shields.io/pypi/v/youbit?color=99ddcc" alt="Package version">
</a>
<a href="#" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/youbit?color=%2399DDCC" alt="Python versions">
</a>
</p>

<p align="center">
    <img src="https://i.imgur.com/SsCzuP3.png" alt="YouBit visual">
    </br>
</p>

YouBit allows you to host any type of file on YouTube.

It does this by creating a video where every pixel represents one or more bits of the original file. When downloaded from YouTube, this video can be decoded back into the original file. [Here's an example of such a video](https://www.youtube.com/watch?v=dnhlx48t-h4).

This is not a novel idea and has been explored by other projects such as [YouTubeDrive](https://github.com/dzhang314/YouTubeDrive) and [fvid](https://github.com/AlfredoSequeida/fvid). However, these projects left alot of good ideas unexplored. YouBit adds a bunch of features, ideas and options to the base concept, while making a reasonable attempt at being performant.
<br><br>


# Installation
```
pip install youbit
```
**NOTE**: If a wheel is not available for your platform, a C compiler needs to be installed prior to installation.
<br><br>

# Usage:  CLI
Encode and upload a file:
```
python -m youbit upload C:/myfile.txt firefox
```
**NOTE**: If you want YouBit to upload video's for you, **chrome** needs to be installed.
The 'firefox' argument denotes which browser YouBit should extract cookies from to authenticate itself with YouTube.
In this example, the currently logged-in account in *firefox* will be used. Can be any of ('firefox', 'chrome', 'edge', 'brave', 'opera', 'chromium').
*Make sure* this account has gone to [studio.youtube.com](https://studio.youtube.com) before using it with YouBit.
When going there for the first time, some popups might appear to ask for things like a channel name. YouBit will not traverse these for you.
<br><br>

Download and decode a YouBit video:
```
python -m youbit download https://youtu.be/dQw4w9WgXcQ
```
Output is always saved in the current working directory unless specified otherwise.
<br><br>

Decode a a local video:
```
python -m decode C:/myvideo.mp4
```
**NOTE**: This video *needs* to have been downloaded from YouTube. You cannot encode a file, and then immeadiately decode just to test it out.
<br><br>

Encode a file without uploading:
```
python -m encode C:/myfile.txt
```
<br><br>


# Usage: Python API
Alternatively, the Python API can be used directly:
```py
from youbit import Encoder

with Encoder('C:/myfile.txt') as encoder:
    encoder.encode()
    url = encoder.upload(browser='opera')  # Extract cookies from Opera browser
    print(url)
```

```py
from youbit import Decoder

with Decoder('https://youtu.be/dQw4w9WgXcQ') as decoder:
    decoder.download()
    path = decoder.decode('C:/mydirectory/')  # Save output in 'C:/mydirectory'. Defaults to current working directory.
    print(path)
```

Encode without upload:
```py
from youbit import Encoder

with Encoder('C:/myfile.txt') as encoder:
    path = encoder.encode('C:/mydirectory/')  # Saves output in 'C:/mydirectory'. Defaults to current working directory.
    print(path)
```

Using different settings:
```py
from youbit import Encoder

with Encoder('C:/myfile.txt') as encoder:
    encoder.encode(ecc=32, bpp=2, zero_frame=True, res='hd', 'crf'=18)
    url = encoder.upload(browser='chrome')
    print(url)
```

Decode local file:
```py
from youbit import Decoder

with Decoder('C:/myvideo.mp4') as decoder:
    path = decoder.decode(
        'C:/mydirectory/',  # Save output in 'C:/mydirectory'. Defaults to current working directory.
        ecc = 32,  # The 'ecc' value that was used during encoding.
        bpp = 1,  # The 'bpp' value that was used during encoding.
        zero_frame = False  # Whether or not 'zero frames' were used during encoding.
    )
    print(path)
```
**NOTE**: 'ecc', 'bpp' and 'zero_frame' are 3 pieces of metadata that need to be known to decode a YouBit video.
When YouBit handles the download, it extracts this metadata from the comments of the video automatically.

<br><br>


# FAQ

- [Does this mean infinite, free cloud storage?!](#does-this-mean-infinite-free-cloud-storage)
- [Why no colors?](#why-no-colors)
- [What is 'bpp'?](#what-is-bpp)
- [Why a framerate of 1?](#why-a-framerate-of-1)
- [Why not you use the YouTube API for uploads?](#why-not-use-the-youtube-api-for-uploads)
- [After uploading, how long do I have to wait to download A YouBit video again?](#after-uploading-how-long-do-i-have-to-wait-to-download-a-youbit-video-again)
- [How large can my file be?](#how-large-can-my-file-be)
- [What settings should I use?](#what-settings-should-i-use)
<br><br>

## Does this mean infinite, free cloud storage?!
No.
+ It's slower: encoding and decoding takes time. The files uploaded to YouTube are much larger than the original. YouTube needs to *process* the video.
+ You can't trust it: If YouTube changes some things tomorrow, there's a chance your video can no longer be decoded.

It's just a very fun concept to explore :)
<br><br>

## Why no colors?
Because [chroma subsampling](https://en.wikipedia.org/wiki/Chroma_subsampling) will compress away color information with extreme prejudice. So instead we save all our information in the luminance channel only. This results in greyscale videos, and works much better. It coincidentally makes the encoding and decoding process less complex as well.
<br><br>

## What is 'bpp'?
It stands for 'Bits Per Pixel' and, as you might have guessed, dictates how many bits of information are saved in a single pixel of video. A higher bpp allows for a higher information density - a smaller output video in comparison to the original file.
However, it also introduces more corrupt pixels.

A bpp of 1 means each pixel only has 2 states, 1 and 0, on and off, white and black. This means our greyscale pixels have a value of either 255 (white) or 0 (black). During decoding, YouBit treats anything 128 or more as a 1, and everything below 128 as a 0. This means YouTube's compression needs to change a pixel's value by at least 127 for it to become corrupt.

Now consider a bpp of 2. Two bits have 4 possible states (00,01,10,11). So to represent 2 bits, our pixels need to have 4 possible states as well. Something like (0, 85,170,255). The distance between these is now smaller: a change of only 43 is now required to corrupt the pixel.
<br><br>

## Why a framerate of 1?
I do not know exactly how YouTube decides on the bitrate to allocate to a stream, but it seems to rougly follow their [recommended video bitrates](https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate). All else equal, a video with a framerate of 1 will get the same bitrate as a video with a framerate of 30. See where I'm going with this? More effective bandwith per frame, less compression.

Secondarily, using a framerate of 1 during encoding allows us to **read only [keyframes](https://en.wikipedia.org/wiki/Group_of_pictures)** during the decoding process.
This is *very* important. Testing showed a massive delta in corruption between keyframes and B- or P-frames. Many keyframes would be completely void of any errors, while some B-frames at the end of a [GOP](https://en.wikipedia.org/wiki/Group_of_pictures) would be almost entirely unusable.

If we use a framerate of 1, YouTube will re-encode it as a video with a framerate of 6. This seems to be the minimum on YouTube.
After analyzing the (open) GOP structure of these 6fps video's, it became apparent that just skipping any non-keyframes during the decoding process is not enough. We would see *duplicate* keyframes scattered around. Fortunately, these duplicate keyframes are predicatable. YouBit discards what it knows to be duplicate keyframes during the decoding process.

This *does* mean that YouBit video's that did **not** go through YouTube, **cannot** be decoded.
<br><br>

## Why not use the YouTube API for uploads?
There are 2 reasons. For one, unverified API projects can only upload private video's. These videos are locked to being private and this cannot be changed. This means YouBit links would not be able to be shared between users. (And no, getting this project verified by Google is not an option for obvious reasons).

Secondly, The YouTube Data API v3 works with a quota system: all interactions with the API have an associated cost. Uploading a video costs a staggering 1600 points, out of 10,000 points that are replenished daily. This would limit the user to a measly 6 uploads per day.

Instead YouBit extract cookies from the browser of choice, to authenticate a [Selenium](https://www.selenium.dev/) headless browser instance where the upload process is automated. This is very hacky, adds alot of overhead and is very sensitive to changes to YouTube's DOM, but it is the best we've got.
<br><br>

## After uploading, how long do I have to wait to download A YouBit video again?
This is tricky, since it can take a long while for YouTube to *fully* finish processing a video.
If the video is unavailable because it is still processing (this means not even an SD stream is available yet), YouBit will throw an exception.
If the video is technically available, but the resolution that was specified during the encoding process is not yet available, YouBit will throw an exception.
If neither of the above, YouBit *will* download the video and *attempt* to decode it.

Thus, it is recommended to wait a sufficient amount of time. The highest available video bitrate (VBR) of any uploaded YouBit video can be checked most easily using the CLI:
```
py -m youbit test vbr https://www.youtube.com/watch?v=SLP9mbCuhJc
```
| Resolution (no zero-frame) | VBR settles around |
| ---------- | ------------------ |
| 1920x1080  | 10200              |
| 2560x1440  | 19700              |
| 3890x2160  | 47800              |
| 7680x4320  | 172407             |

The decoding process might very well still work with a lower VBR, it all depends on the settings that were used.
There's no real advantage to using higher resolutions than the default of 1080p.
<br><br>


## How large can my file be?
YouBit encodes your files in chunks, so we are not limited by memory, but we are limited by YouTube's maximum video length.
YouTube video's are allowed to be up to 12 hours long, or 128GB, whichever comes first.
YouBit will raise exceptions during the encoding process if either of these are violated.
(*If the YouTube account you are using is not verified, the limit is 15 minutes instead. Be sure to verify your account.*)

Ofcourse, this depends entirely on the settings selected.
To give you an idea, the default settings will stop working with files larger than **9GB**.
<br><br>


## What is a 'zero frame'?
YouBit has the option to use 'zeroframes'. If enabled, YouBit will interject completely black frames in between real frames when generating the video.
The idea is that YouTube will still allocate the same bitrate, but since the video is twice as long and all-black frames can be compressed away almost entirely, we will have twice the bandwidth per actual data-holding frame. In practice, this only works a little: video's with zero frames have a lower bitrate, but not half. 1080p video's seem to get a bitrate of 7000, compared to the usual 10200.

This is still a useful ~40% effective inrease in effective available bandwidth, leading to less errors and a potentially higher information density.
On higher resolutions however, the use of zero frames seems to be detrimental. Use at your own discretion.
<br><br>


## What settings should I use?
Unless you know exactly what *all* the options do and how they interact, I would advise you to stick to the defaults.
Not to say that the defaults settings are the best, they are just the simplest and most reliable.
You can actually speed up the whole process (encode -> upload -> download -> decode) significantly by using different settings.

For example, setting 'zero_frame' to True allows you to use a 'bpp' of 2, which drastically speeds the whole process, since the resulting video is half the size. 😉
