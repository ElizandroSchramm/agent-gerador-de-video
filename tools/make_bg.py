# tools/make_bg.py
# Usage:
#   python tools/make_bg.py --out assets/bg.png
from PIL import Image, ImageDraw, ImageFont
import argparse, os

def make_gradient(w, h, c1=(16,16,18), c2=(255,120,60)):
    img = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h))
    return Image.composite(top, img, mask)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/bg.png")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img = make_gradient(1080, 1920)
    img.save(args.out, "PNG")
    print(f"[ok] BG salvo em {args.out}")
