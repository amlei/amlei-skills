# FFmpeg recipes

## Probe

```bash
ffprobe -v error -show_entries \
  format=duration,size:stream=codec_type,width,height \
  -of json final.mp4
```

## Fit 16:9 source into 9:16 with frosted background

```text
[0:v]crop=1138:640:400:100,split=2[bgsrc][fgsrc];
[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
gblur=sigma=28,eq=brightness=-0.08,format=rgba,
colorchannelmixer=aa=0.7[bgalpha];
color=c=black:s=1080x1920:r=30,trim=duration=DURATION,setpts=PTS-STARTPTS[black];
[black][bgalpha]overlay=0:0[bgfinal];
[fgsrc]scale=1080:1920:force_original_aspect_ratio=decrease,
tpad=stop_mode=clone:stop_duration=10[fgfinal];
[bgfinal][fgfinal]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[v]
```

`aa=0.7` means the background is 70% opaque / 30% transparent.

## Direct-cut concat

```bash
ffmpeg -f concat -safe 0 -i concat.txt -c copy visual.mp4
```

## Package with narration

```bash
ffmpeg -i visual.mp4 -i voice.m4a \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k \
  -shortest final.mp4
```

## QC contact sheet

```bash
ffmpeg -i final.mp4 \
  -vf "fps=1/10,scale=240:427,tile=5x6" \
  -frames:v 1 contact.jpg
```
