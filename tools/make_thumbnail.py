# tools/make_thumbnail.py
# Usage:
#   python tools/make_thumbnail.py --title "AGENTE EM 1 NOITE" --subtitle "Spark Pro | Agno" --out assets/thumbnail.png
# Requires: pip install pillow
from PIL import Image, ImageDraw, ImageFont
import argparse, os

def make_gradient(w, h, c1=(22, 22, 22), c2=(255, 90, 0)):
    img = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.linear_gradient("L").resize((w, h)).rotate(90, expand=0)
    return Image.composite(top, img, mask)

def get_text_size(draw, text, font):
    """Compatível com Pillow >=10 e <10."""
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        w, h = draw.textsize(text, font=font)
    return w, h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out", default="assets/thumbnail.png")
    args = ap.parse_args()

    W, H = 1080, 1080
    img = make_gradient(W, H)
    draw = ImageDraw.Draw(img)

    # Fontes padrão
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 48)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Título
    tw, th = get_text_size(draw, args.title, font_title)
    draw.text(((W - tw) // 2, H // 2 - th - 10), args.title, font=font_title, fill=(255, 255, 255))

    # Subtítulo
    if args.subtitle:
        sw, sh = get_text_size(draw, args.subtitle, font_sub)
        draw.text(((W - sw) // 2, H // 2 + 10), args.subtitle, font=font_sub, fill=(240, 240, 240))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img.save(args.out, "PNG")
    print(f"[ok] Thumbnail salva em {args.out}")

if __name__ == "__main__":
    main()
