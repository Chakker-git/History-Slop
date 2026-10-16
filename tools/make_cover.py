#!/usr/bin/env python3
"""Generate cover.jpg (3000x3000, Apple Podcasts spec) for History Slop.

Usage: python3 tools/make_cover.py [out.jpg]
"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W = 3000
INK, CREAM, RED, DIM = (22, 20, 15), (239, 230, 210), (200, 67, 43), (150, 140, 120)
SERIF = "/usr/share/texmf/fonts/opentype/public/lm/lmroman10-bold.otf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
rng = random.Random(751)  # Talas


def centred(d, y, text, font, fill, tracking=0):
    if tracking:
        widths = [d.textlength(c, font=font) for c in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = (W - total) / 2
        for c, w in zip(text, widths):
            d.text((x, y), c, font=font, fill=fill)
            x += w + tracking
    else:
        w = d.textlength(text, font=font)
        d.text(((W - w) / 2, y), text, font=font, fill=fill)


def main(out):
    img = Image.new("RGB", (W, W), INK)
    # soft vignette
    vig = Image.new("L", (W, W), 0)
    ImageDraw.Draw(vig).ellipse((-400, -300, W + 400, W + 500), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(500))
    img = Image.composite(Image.new("RGB", (W, W), (38, 34, 26)), img, vig)
    d = ImageDraw.Draw(img)

    # thin frame
    m = 130
    d.rectangle((m, m, W - m, W - m), outline=DIM, width=6)
    d.rectangle((m + 22, m + 22, W - m - 22, W - m - 22), outline=(70, 64, 52), width=3)

    centred(d, 330, "ANNA & RUNE", ImageFont.truetype(SANS_B, 110), DIM, tracking=38)
    size = 640
    while ImageFont.truetype(SERIF, size).getlength("HISTORY") > W - 2 * 330:
        size -= 10
    hf = ImageFont.truetype(SERIF, size)
    centred(d, 560, "HISTORY", hf, CREAM)

    # rubber-stamp "SLOP"
    SW, SH = 1700, 680
    st = Image.new("L", (SW, SH), 0)
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((30, 30, SW - 30, SH - 30), radius=40, outline=255, width=44)
    f = ImageFont.truetype(SERIF, 440)
    l, t, r, b = sd.textbbox((0, 0), "SLOP", font=f)
    sd.text(((SW - (r - l)) / 2 - l, (SH - (b - t)) / 2 - t), "SLOP", font=f, fill=255)
    noise = Image.effect_noise(st.size, 120).point(lambda v: 255 if v > 70 else 0)
    st = ImageChops.multiply(st, noise.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 90 else 0))
    st = st.rotate(-6, expand=True, resample=Image.BICUBIC)
    img.paste(Image.new("RGB", st.size, RED), ((W - st.width) // 2, 1260), st)

    # waveform with crenellated tops
    base, n, gap = 2540, 40, 26
    bw = (W - 2 * 330 - gap * (n - 1)) / n
    for i in range(n):
        x = 330 + i * (bw + gap)
        env = math.sin(math.pi * (i + 0.5) / n) ** 0.7
        h = 30 + env * (90 + rng.random() * 170)
        d.rectangle((x, base - h, x + bw, base), fill=CREAM if i % 9 else RED)
    centred(d, 2640, "Long-form history.  Synthetic voices.  Real footnotes.",
            ImageFont.truetype(SANS, 92), DIM)

    img.save(out, "JPEG", quality=88, optimize=True, progressive=False)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cover.jpg")
