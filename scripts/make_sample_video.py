#!/usr/bin/env python3
"""Regenerate templates/assets/video/sample-ambient-loop.webm, an abstract 8 second loop
used to preview hero-fullbleed and video-block before the client supplies real footage.

Needs Python Playwright and the ffmpeg that Playwright installs (ms-playwright/ffmpeg-*).
    py -3.11 make_sample_video.py
The clip is drawn by this script (moving light blobs on a dark grid), so it carries no third-party content.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "templates" / "assets" / "video" / "sample-ambient-loop.webm"
LOOP = 8

HTML = """<!doctype html><html><head><style>
html,body{margin:0;height:100%;overflow:hidden;background:#0b1220}
.stage{position:absolute;inset:0;overflow:hidden}
.grid{position:absolute;inset:-10%;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:64px 64px;animation:pan LOOPs linear infinite}
.b{position:absolute;border-radius:50%;filter:blur(70px);opacity:.75;mix-blend-mode:screen}
.b1{width:620px;height:620px;background:#2f6bff;left:8%;top:10%;animation:o1 LOOPs linear infinite}
.b2{width:520px;height:520px;background:#21c7b5;left:55%;top:35%;animation:o2 LOOPs linear infinite}
.b3{width:460px;height:460px;background:#f06a3c;left:35%;top:-10%;animation:o3 LOOPs linear infinite;opacity:.55}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.35) 1px,transparent 1.5px);background-size:32px 32px;opacity:.25;animation:pan2 LOOPs linear infinite}
@keyframes pan{to{transform:translate(64px,64px)}}
@keyframes pan2{to{transform:translate(-32px,32px)}}
@keyframes o1{0%{transform:rotate(0deg) translateX(90px) rotate(0deg)}100%{transform:rotate(360deg) translateX(90px) rotate(-360deg)}}
@keyframes o2{0%{transform:rotate(0deg) translateY(110px) rotate(0deg)}100%{transform:rotate(-360deg) translateY(110px) rotate(360deg)}}
@keyframes o3{0%{transform:rotate(0deg) translate(70px,40px) rotate(0deg)}100%{transform:rotate(360deg) translate(70px,40px) rotate(-360deg)}}
</style></head><body><div class="stage"><div class="grid"></div><div class="b b1"></div><div class="b b2"></div><div class="b b3"></div><div class="dots"></div></div></body></html>""".replace("LOOP", str(LOOP))


def main():
    ffmpegs = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright", "ffmpeg-*", "ffmpeg*")) + glob.glob(os.path.expanduser("~/.cache/ms-playwright/ffmpeg-*/ffmpeg*"))
    if not ffmpegs:
        print("ffmpeg from Playwright not found. Run: python -m playwright install ffmpeg")
        return 1
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 720}, screen={"width": 1280, "height": 720}, device_scale_factor=1, record_video_dir=str(tmp), record_video_size={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.set_content(HTML)
        page.wait_for_timeout((LOOP + 2) * 1000 + 500)
        ctx.close()
        b.close()
    raw = next(tmp.glob("*.webm"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Some browsers draw the page smaller than the recording frame and pad it with gray.
    # Find the painted area in one frame and crop to a centered 16:9 box inside it.
    from PIL import Image
    probe = tmp / "probe.png"
    subprocess.run([ffmpegs[0], "-y", "-hide_banner", "-loglevel", "error", "-ss", "3", "-i", str(raw), "-frames:v", "1", str(probe)], check=True)
    im = Image.open(probe).convert("RGB")
    W, H = im.size
    gray = lambda px: all(abs(c - 128) <= 4 for c in px)
    right = max(x for x in range(W) if not gray(im.getpixel((x, H // 3))))
    bottom = max(y for y in range(H) if not gray(im.getpixel((W // 3, y))))
    cw, ch = right + 1, bottom + 1
    if cw / ch > 16 / 9:
        tw, th = int(ch * 16 / 9) // 2 * 2, ch // 2 * 2
    else:
        tw, th = cw // 2 * 2, int(cw * 9 / 16) // 2 * 2
    x0, y0 = (cw - tw) // 2, (ch - th) // 2
    vf = "crop=%d:%d:%d:%d,scale=1280:720" % (tw, th, x0, y0)
    cmd = [ffmpegs[0], "-y", "-hide_banner", "-loglevel", "error", "-ss", "1.5", "-i", str(raw), "-t", str(LOOP), "-an", "-vf", vf,
           "-c:v", "libvpx", "-b:v", "900k", "-crf", "20", "-auto-alt-ref", "0", str(OUT)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote %s (%d KB)" % (OUT, OUT.stat().st_size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
