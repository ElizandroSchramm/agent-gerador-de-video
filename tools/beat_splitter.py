# tools/beat_splitter.py
import argparse
from pathlib import Path
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
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", default="beats.txt")
    ap.add_argument("--max", type=int, default=6)
    args = ap.parse_args()
    text = Path(args.script).read_text(encoding="utf-8")
    beats = extract_beats(text, args.max)
    Path(args.out).write_text("\n\n---\n\n".join(beats), encoding="utf-8")
    print(f"[ok] {len(beats)} beats salvos em {args.out}")
