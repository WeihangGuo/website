# Cover media

The homepage uses 16 preprocessed assets: 11 looping GIFs and 5 WebP images.
All 8 source videos and the 3 existing GIFs retain their full timelines.
GIFs use 6–10 fps, a 224–400 px maximum dimension, and optimized palettes.
The iPhone HLG footage is converted to SDR. Image metadata and audio are omitted.

`posters/` supplies still images for reduced motion, pause, offscreen playback, and GIF loading failures.
The source files are preserved in the local, gitignored `originals/` folder.

Rebuild from the repository root with `python3 build_cover.py` (requires ffmpeg, ffprobe, and Pillow).
Use `python3 build_cover.py --force` to regenerate every asset.
`manifest.json` records the source mapping, dimensions, durations, and exact sizes.

| Asset | Original |
| --- | --- |
| `cover_1.webp` | `4FEE56A5-35EF-4973-98BD-9F62C4B7A0D3.JPG` |
| `cover_2.webp` | `IMG_1131.HEIC` |
| `cover_3.gif` | `IMG_3039.mov` |
| `cover_4.webp` | `IMG_3416.jpg` |
| `cover_5.gif` | `IMG_3447.mov` |
| `cover_6.webp` | `IMG_4414.HEIC` |
| `cover_7.gif` | `IMG_4549.mov` |
| `cover_8.gif` | `IMG_4790.mov` |
| `cover_9.gif` | `arm_avoidance.mp4` |
| `cover_10.gif` | `guo2025castl.gif` |
| `cover_11.webp` | `guo2026omplbinding.png` |
| `cover_12.gif` | `ompl-vamp-combined.gif` |
| `cover_13.gif` | `rice_cup.mov` |
| `cover_14.gif` | `rice_unfold.mov` |
| `cover_15.gif` | `two_arm_doorway_2x.mp4` |
| `cover_16.gif` | `yan2025using.gif` |
