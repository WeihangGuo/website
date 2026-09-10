#!/usr/bin/env python3
"""Prepare the cover collage with ffmpeg, ffprobe, and Pillow.

Run: python3 build_cover.py
Original media is kept locally in images/cover_page/originals (gitignored).
GIFs retain the complete source timeline. No audio or metadata is published.
"""

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent / "images" / "cover_page"
SOURCES = [
    ("4FEE56A5-35EF-4973-98BD-9F62C4B7A0D3.JPG", "Autonomous racing robots"),
    ("IMG_1131.HEIC", "Autonomous vehicle electronics"),
    ("IMG_3039.mov", "Robot arm manipulating objects at a desk"),
    ("IMG_3416.jpg", "Underwater robot in a pool"),
    ("IMG_3447.mov", "Robot arm picking up objects"),
    ("IMG_4414.HEIC", "Robot calibration in the lab"),
    ("IMG_4549.mov", "Robot motion planning and its simulation"),
    ("IMG_4790.mov", "Interactive robot simulation"),
    ("arm_avoidance.mp4", "Robot arm obstacle avoidance"),
    ("guo2025castl.gif", "Constrained robot manipulation"),
    ("guo2026omplbinding.png", "Motion planning for multiple manipulators"),
    ("ompl-vamp-combined.gif", "Real-time motion planning"),
    ("rice_cup.mov", "Two robot arms manipulating a cup"),
    ("rice_unfold.mov", "Two robot arms unfolding a Rice shirt"),
    ("two_arm_doorway_2x.mp4", "Coordinated robot motion through a doorway"),
    ("yan2025using.gif", "Task and motion planning simulation"),
]


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "quiet", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,color_transfer:format=duration",
        "-of", "json", str(path),
    ]))


def hlg_lut(path):
    """HLG / BT.2020 to SDR / BT.709 for ffmpeg builds without libzimg."""
    def linear(value):
        return value * value / 3 if value <= .5 else (math.exp((value - .55991073) / .17883277) + .28466892) / 12

    def srgb(value):
        value = max(0, min(1, value))
        return 12.92 * value if value <= .0031308 else 1.055 * value ** (1 / 2.4) - .055

    with path.open("w") as file:
        file.write("LUT_3D_SIZE 33\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
        for b in range(33):
            for g in range(33):
                for r in range(33):
                    rgb = [linear(v / 32) for v in (r, g, b)]
                    luminance = sum(a * v for a, v in zip((.2627, .6780, .0593), rgb))
                    gain = luminance ** .2 * (1000 / 203) if luminance else 0
                    red, green, blue = [v * gain for v in rgb]
                    converted = (1.6605 * red - .5876 * green - .0728 * blue,
                                 -.1246 * red + 1.1329 * green - .0083 * blue,
                                 -.0182 * red - .1006 * green + 1.1187 * blue)
                    y = luminance * gain
                    tone = (1 + y / 25) / (1 + y)
                    file.write(" ".join(f"{srgb(v * tone):.6f}" for v in converted) + "\n")


def prepare(force=False):
    originals = ROOT / "originals"
    posters = ROOT / "posters"
    originals.mkdir(exist_ok=True)
    posters.mkdir(exist_ok=True)
    previous = {item['id']: item for item in json.loads((ROOT / 'manifest.json').read_text())} if (ROOT / 'manifest.json').exists() else {}
    manifest = []
    for number, (name, description) in enumerate(SOURCES, 1):
        source = originals / name
        if not source.exists():
            shutil.move(ROOT / name, source)
        animated = source.suffix.lower() in {".mov", ".mp4", ".gif"}
        destination = ROOT / f"cover_{number}.{'gif' if animated else 'webp'}"
        record = {"id": number, "source": name, "description": description,
                  "file": destination.name, "source_bytes": source.stat().st_size}

        with tempfile.TemporaryDirectory(prefix="cover-") as tmp:
            still = Path(tmp) / "frame.png"
            if animated:
                metadata = probe(source)
                transfer = metadata["streams"][0].get("color_transfer")
                # iPhone HDR footage needs conversion to SDR before palette generation.
                tone = ""
                if transfer == "arib-std-b67":
                    lut = Path(tmp) / "hlg.cube"
                    hlg_lut(lut)
                    tone = f"format=rgb24,lut3d=file='{lut}':interp=tetrahedral,"
                profiles = [(400, 10, 128), (320, 8, 96), (256, 8, 80), (224, 6, 64)]
                old = previous.get(number)
                # Completed small assets do not need another lossy encode.
                if (not force and old and destination.exists()
                        and old['source_bytes'] == source.stat().st_size
                        and source.stat().st_mtime <= destination.stat().st_mtime
                        and (destination.stat().st_size <= 1_500_000
                             or (old.get('fps') == 6 and max(old['width'], old['height']) <= 224))):
                    manifest.append(old)
                    continue
                if old and not force:
                    profiles = [profile for profile in profiles if profile[0] <= max(old['width'], old['height'])]
                encoded = Path(tmp) / destination.name
                for width, fps, colors in profiles:
                    base = (f"fps={fps},scale={width}:{width}:force_original_aspect_ratio=decrease:"
                            f"flags=lanczos,{tone}setsar=1")
                    filters = (f"[0:v:0]{base},split[frames][palette_input];"
                               f"[palette_input]palettegen=max_colors={colors}:stats_mode=diff[palette];"
                               "[frames][palette]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle")
                    ffmpeg("-i", source, "-filter_complex", filters, "-an", "-map_metadata", "-1",
                           "-loop", "0", encoded)
                    if encoded.stat().st_size <= 1_500_000:
                        break
                encoded.replace(destination)
                ffmpeg("-i", destination, "-frames:v", "1", still)
                poster = posters / f"cover_{number}.jpg"
                with Image.open(still) as image:
                    image.convert("RGB").save(poster, quality=83, optimize=True)
                record.update(poster=f"posters/{poster.name}", fps=fps, colors=colors,
                              source_duration=float(metadata["format"]["duration"]),
                              duration=float(probe(destination)["format"]["duration"]))
            else:
                # ffmpeg reconstructs HEIC image grids and applies their orientation.
                if source.suffix.lower() == ".heic":
                    ffmpeg("-i", source, "-frames:v", "1", still)
                    image_source = still
                else:
                    image_source = source
                with Image.open(image_source) as image:
                    image = ImageOps.exif_transpose(image).convert("RGB")
                    image.thumbnail((720, 720), Image.Resampling.LANCZOS)
                    image.save(destination, "WEBP", quality=83, method=6)
                record["poster"] = destination.name
        with Image.open(destination) as image:
            record.update(width=image.width, height=image.height)
        record["bytes"] = destination.stat().st_size
        manifest.append(record)
        print(f"{name} -> {destination.name}: {record['bytes'] / 1024:.0f} KB", flush=True)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Total: {sum(item['bytes'] for item in manifest) / 1024**2:.2f} MiB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true', help='Regenerate all media from the originals.')
    prepare(force=parser.parse_args().force)
