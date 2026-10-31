# -*- coding: utf-8 -*-
"""M1 样板截图：320 / 390 / 430 三档手机 + 1080x1440 分享卡。

Edge headless 的 window-size 与实际 CSS viewport 存在偏移（窗口边框/滚动条），
直接截图会导致右侧被裁。这里用固定宽度 iframe 承载页面：
- iframe 的 CSS 宽度 = 目标宽度（页面媒体查询以此为准）
- 外层窗口开得更大，截图后按 iframe 区域裁切
因此输出像素宽度精确等于目标宽度。
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SHOTS = ROOT / "shots"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
PROFILE = SHOTS / "_edgeprofile_shots"
WRAP = SITE / "_shot_wrap.html"
CSS_HEIGHT = 1000

PAGES = [
    ("index", "index.html"),
    ("event", "event.html"),
    ("schedule", "schedule.html"),
    ("match", "matches/s2-first.html"),
    ("player", "players/fangshan-de-qiu.html"),
    ("sources", "sources.html"),
]
WIDTHS = [320, 390, 430]

WRAPPER = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:#000}iframe{border:0;display:block;width:%W%px;height:%H%px}</style>
</head><body><iframe src="%SRC%" scrolling="no"></iframe></body></html>"""


def raw_shot(page: str, css_w: int, css_h: int, out: Path) -> None:
    WRAP.write_text(WRAPPER.replace("%W%", str(css_w)).replace("%H%", str(css_h)).replace("%SRC%", page),
                    encoding="utf-8")
    cmd = [str(EDGE), "--headless", "--disable-gpu", "--hide-scrollbars",
           f"--user-data-dir={PROFILE}", "--no-first-run", "--no-default-browser-check",
           "--force-device-scale-factor=1", f"--window-size=1400,{max(1200, css_h + 200)}",
           f"--screenshot={out}", WRAP.resolve().as_uri()]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    if not out.exists():
        raise RuntimeError(f"screenshot missing: {out}")


def shot(page: str, css_w: int, css_h: int, out: Path) -> None:
    tmp = SHOTS / "_raw.png"
    raw_shot(page, css_w, css_h, tmp)
    im = Image.open(tmp).convert("RGB")
    if im.width < css_w or im.height < css_h:
        raise RuntimeError(f"raw too small for {page} {css_w}: {im.size}")
    im.crop((0, 0, css_w, css_h)).save(out)
    tmp.unlink(missing_ok=True)


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    try:
        for slug, page in PAGES:
            imgs = []
            for w in WIDTHS:
                out = SHOTS / f"{slug}-{w}.png"
                shot(page, w, CSS_HEIGHT, out)
                imgs.append(Image.open(out).convert("RGB"))
                print(slug, w, out.stat().st_size)
            gap, margin, label_h = 14, 14, 24
            h = max(im.height for im in imgs)
            total_w = margin * 2 + sum(im.width for im in imgs) + gap * 2
            canvas = Image.new("RGB", (total_w, h + label_h + margin), (16, 18, 24))
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
            except Exception:
                font = ImageFont.load_default()
            x = margin
            for w, im in zip(WIDTHS, imgs):
                draw.text((x, 4), f"{w}px", fill=(232, 168, 50), font=font)
                canvas.paste(im, (x, label_h))
                x += im.width + gap
            canvas.save(SHOTS / f"{slug}-three-widths.png")
        share = SHOTS / "share-card-1080x1440.png"
        shot("share-card.html", 1080, 1440, share)
        print("share card", Image.open(share).size)
    finally:
        WRAP.unlink(missing_ok=True)
        shutil.rmtree(PROFILE, ignore_errors=True)


if __name__ == "__main__":
    main()
