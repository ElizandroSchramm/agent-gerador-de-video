# tools/generate_storyboard.py
import argparse, os, base64, re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def split_sentences(text):
    parts = [p.strip() for p in SENT_SPLIT.split(text) if p.strip()]
    return parts

def extract_beats(text, max_beats=6):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    beats, buf = [], []
    for ln in lines:
        if ln.startswith("[") and ln.endswith("]"):
            if buf: beats.append(" ".join(buf)); buf = []
        else:
            buf.append(ln)
    if buf: beats.append(" ".join(buf))
    if len(beats) > max_beats:
        beats = beats[:max_beats-1] + ["Resumo visual do CTA"]
    return beats[:max_beats]

def ensure_min_scenes(text, beats, min_scenes):
    if len(beats) >= min_scenes:
        return beats[:min_scenes]
    # tenta enriquecer com sentenças do texto
    sentences = split_sentences(text)
    i = 0
    while len(beats) < min_scenes and i < len(sentences):
        s = sentences[i]
        if s not in beats and not s.startswith("["):
            beats.append(s)
        i += 1
    # se ainda faltar, duplica o último
    while len(beats) < min_scenes and beats:
        beats.append(beats[-1])
    return beats[:min_scenes]

def main():
    from openai import OpenAI
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--outdir", default="assets/slides")
    ap.add_argument("--style", default="Clean tech, minimal, depth of field, no text on image")
    ap.add_argument("--brand", default="Generic")
    ap.add_argument("--model", default=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"))
    ap.add_argument("--min_scenes", type=int, default=5, help="Número mínimo de imagens a gerar")
    args = ap.parse_args()

    text = Path(args.script).read_text(encoding="utf-8")
    beats = extract_beats(text, max_beats=args.min_scenes)
    beats = ensure_min_scenes(text, beats, args.min_scenes)

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    prompt_base = f"Generate a 1024x1536 illustration with consistent style (no words/text). Brand mood: {args.brand}. Style: {args.style}."
    client = OpenAI()

    for i, beat in enumerate(beats, 1):
        prompt = prompt_base + f" Scene {i}: {beat}"
        img = client.images.generate(model=args.model, prompt=prompt, size="1024x1536", quality="high", n=1)
        b64 = img.data[0].b64_json
        (outdir / f"slide_{i:02d}.png").write_bytes(base64.b64decode(b64))
        print(f"[ok] slide_{i:02d}.png")

if __name__ == "__main__":
    main()
