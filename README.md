<p align="center">
    <img src="https://i.imgur.com/SsCzuP3.png" alt="YouBit visual">
    </br>
</p>

YouBit allows you to host any type of file on YouTube.

It does this by creating a video where every pixel represents one or more bits of the original file. When downloaded from YouTube, this video can be decoded back into the original file.

This is not a novel idea and has been explored by other projects such as [YouTubeDrive](https://github.com/dzhang314/YouTubeDrive) and [fvid](https://github.com/AlfredoSequeida/fvid). However, these projects left alot of good ideas unexplored. YouBit adds a bunch of features, ideas and options to the base concept, while making a reasonable attempt at being performant.


# Installation
YouBit is a package first, ...


# Usage
sdfsdfsdfsdf


---


# FAQ

- [Does this mean infinite, free cloud storage?!](#does-this-mean-infinite-free-cloud-storage)
- [Why no colors?](#why-no-colors)
- [What is 'bpp'?](#what-is-bpp)
- [Why a framerate of 1?](#why-a-framerate-of-1)
- [Why not you use the YouTube API for uploads?](#why-not-use-the-youtube-api-for-uploads)
- [After uploading, how long do I have to wait to download A YouBit video again?](#after-uploading-how-long-do-i-have-to-wait-to-download-a-youbit-video-again)
- [How large can my file be?](#how-large-can-my-file-be)
- [What options should I use?](#what-options-should-i-use)


## Does this mean infinite, free cloud storage?!
No.
+ It's slower: encoding and decoding takes time. The files uploaded to YouTube are much larger than the original. YouTube needs to *process* the video.
+ You can't trust it: If YouTube changes some things tomorrow, there's a chance your video can no longer be decoded.

It's just a very fun concept to explore :)

## Why no colors?
Because [chroma subsampling](https://en.wikipedia.org/wiki/Chroma_subsampling) will compress away color information with extreme prejudice. So instead we save all our information in the luminance channel only. This results in greyscale videos, and works much better. It coincidentally makes the encoding and decoding process less complex as well.

## What is 'bpp'?
It stands for 'Bits Per Pixel' and, as you might have guessed, dictates how many bits of information are saved in a single pixel of video. A higher bpp allows for a higher information density - a smaller output video in comparison to the original file.
However, it also introduces more corrupt pixels.

A bpp of 1 means each pixel only has 2 states, 1 and 0, on and off, white and black. This means our greyscale pixels have a value of either 255 (white) or 0 (black). During decoding, YouBit treats anything 128 or more as a 1, and everything below 128 as a 0. This means YouTube's compression needs to change a pixel's value by at least 127 for it to become corrupt.

Now consider a bpp of 2. Two bits have 4 possible states (00,01,10,11). So to represent 2 bits, our pixels need to have 4 possible states as well. Something like (0, 85,170,255). The distance between these is now smaller: a change of only 43 is now required to corrupt the pixel.

## Why a framerate of 1?
I do not know exactly how YouTube decides on the bitrate to allocate to a stream, but it seems to rougly follow their [recommended video bitrates](https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate). All else equal, a video with a framerate of 1 will get the same bitrate as a video with a framerate of 30. See where I'm going with this? More effective bandwith per frame, less compression.

Secondarily, using a framerate of 1 during encoding allows us to **read only [keyframes](https://en.wikipedia.org/wiki/Group_of_pictures)** during the decoding process.
This is *very* important. Testing showed a massive delta in corruption between keyframes and B- or P-frames. Many keyframes would be completely void of any errors, while some B-frames at the end of a [GOP](https://en.wikipedia.org/wiki/Group_of_pictures) would be almost entirely unusable.

If we use a framerate of 1, YouTube will re-encode it as a video with a framerate of 6. This seems to be the minimum on YouTube.
After analyzing the (open) GOP structure of these 6fps video's, it became apparent that just skipping any non-keyframes during the decoding process is not enough. We would see *duplicate* keyframes scattered around. Fortunately, these duplicate keyframes are predicatable. YouBit discards what it knows to be duplicate keyframes during the decoding process.

This *does* mean that YouBit video's that did **not** go through YouTube, **cannot** be decoded.

## Why not use the YouTube API for uploads?
There are 2 reasons. For one, unverified API projects can only upload private video's. These videos are locked to being private and this cannot be changed. This means YouBit links would not be able to be shared between users. (And no, getting this project verified by Google is not an option for obvious reasons).

Secondly, The YouTube Data API v3 works with a quota system: all interactions with the API have an associated cost. Uploading a video costs a staggering 1600 points, out of 10,000 points that are replenished daily. This would limit the user to a measly 6 uploads per day.

Instead YouBit extract cookies from the browser of choice, to authenticate a [Selenium](https://www.selenium.dev/) headless browser instance where the upload process is automated. This is very hacky, adds alot of overhead and is very sensitive to changes to YouTube's DOM, but it is the best we've got.

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

> There's no real advantage to using higher resolutions than the default of 1080p.


## How large can my file be?
YouBit encodes your files in chunks, so we are not limited by memory, but we are limited by YouTube's maximum video length.
YouTube video's are allowed to be up to 12 hours long, or 128GB, whichever comes first.
YouBit will raise exceptions during the encoding process if either of these are violated.
(*If the YouTube account you are using is not verified, the limit is 15 minutes instead. Be sure to verify your account.*)

Ofcourse, this depends entirely on the settings selected.
To give you an idea, the default settings will stop working with files larger than **9GB**.


## What is a 'zero frame'?
YouBit has the option to use 'zeroframes'. If enabled, YouBit will interject completely black frames in between real frames when generating the video.
The idea is that YouTube will still allocate the same bitrate, but since the video is twice as long and all-black frames can be compressed away almost entirely, we will have twice the bandwidth per actual data-holding frame. In practice, this only works a little: video's with zero frames have a lower bitrate, but not half. 1080p video's seem to get a bitrate of 7000, compared to the usual 10200.

This is still a useful ~40% effective inrease in effective available bandwidth, leading to less errors and a potentially higher information density.
> On higher resolutions however, the use of zero frames seems to be detrimental. Use at your own discretion.


## What options should I use?
The default ones.
