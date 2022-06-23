<p align="center">
    <img src="https://i.imgur.com/SsCzuP3.png" alt="YouBit visual">
    </br>
</p>

YouBit allows you to host any type of file on YouTube.

It does this by creating a video where every pixel represents one or more bits of the original file. When downloaded from YouTube, this video can be decoded back into the original file.

This is not a novel idea and has been explored by other projects such as [YouTubeDrive](https://github.com/dzhang314/YouTubeDrive) and [fvid](https://github.com/AlfredoSequeida/fvid). However, these projects left alot of good ideas unexplored.
// something more about what youbit does better without making it too long]


# Installation
sdfqsdfqsdf


# Usage
sdfsdfsdfsdf


# FAQ

- [Why no colors?](#why-no-colors)
- [What is 'bpp'?](#what-is-bpp)
- [Why a framerate of 1?](#why-a-framerate-of-1)
- [Why not you use the YouTube API for uploads?](#why-not-use-the-youtube-api-for-uploads)
- [After uploading, how long do I have to wait to download A YouBit video again?](#after-uploading-how-long-do-i-have-to-wait-to-download-a-youbit-video-again)


## Why no colors?
Because [chroma subsampling](https://en.wikipedia.org/wiki/Chroma_subsampling) will compress away color information with extreme prejudice. So instead we save all our information in the luminance channel only. This results in greyscale videos, and works much better. It coincidentally makes the encoding and decoding process less complex as well.

## What is 'bpp'?
It stands for 'Bits Per Pixel' and, as you might have guessed, dictates how many bits of information are saved in a single pixel of video. A higher bpp allows for a higher information density - a smaller output video in comparison to the original file.
However, it also introduces more corrupt pixels.

A bpp of 1 means each pixel only has 2 states, 1 and 0, on and off, white and black. This means our greyscale pixels have a value of either 255 (white) or 0 (black). During decoding, YouBit treats anything 128 or more as a 1, and everything below 128 as a 0. This means YouTube's compression needs to change a pixel's value by at least 127 for it to become corrupt.

Now consider a bpp of 2. Two bits have 4 possible states (00,01,10,11). So to represent 2 bits, our pixels need to have 4 possible states as well. Something like (0, 85,170,255). The distance between these is now smaller: a change of only 43 is now required to corrupt the pixel.

## Why a framerate of 1?
I do not know exactly how YouTube decides on the bitrate to allocate to a stream, but it seems to rougly follow their [recommended video bitrates](https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate). All else equal, a video with a framerate of 1 will get the same bitrate as a video with a framerate of 30. See where I'm going with this? More effective bandwith per frame, less compression.
(I've tried injecting all-black frames between actual frames

## Why not use the YouTube API for uploads?
There are 2 reasons. For one, unverified API projects can only upload private video's. These videos are locked to being private and this cannot be changed. This means YouBit links would not be able to be shared between users. (And no, getting this project verified by Google is not an option for obvious reasons).

Secondly, The YouTube Data API v3 works with a quota system: all interactions with the API have an associated cost. Uploading a video costs a staggering 1600 points, out of 10,000 points that are replenished daily. This would limit the user to a measly 6 uploads per day.

Instead YouBit extract cookies from the browser of choice, to authenticate a [Selenium](https://www.selenium.dev/) headless browser instance where the upload process is automated. This is very hacky, adds alot of overhead and is very sensitive to changes to YouTube's DOM, but it is the best we've got.

## After uploading, how long do I have to wait to download A YouBit video again?
This is tricky, since it can take a long while for YouTube to *fully* finish processing a video.
If the video is unavailable because it is still processing (this means not even an SD stream is available yet), YouBit will throw an exception.
If the video is technically available, but the resolution that was specified during the encoding process is not yet available, YouBit will throw an exception.
If neither of the above, YouBit *will* download the video and attempt to decode it. If the video bitrate is under 6000, YouBit will raise a warning to tell you that sucesfully decoding the video is unlikely.

Thus, it is recommended to wait a sufficient amount of time. The highest available video bitrate of any uploaded YouBit video can be checked most easily using the CLI:
```
py -m youbit test vbr https://www.youtube.com/watch?v=SLP9mbCuhJc
```
A normal YouBit video will settle around 10233, a YouBit video with the 'zero frame' option enabled will settle around 7000.

## //zero frame//
lorem ipsum
