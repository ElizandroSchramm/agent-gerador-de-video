# run_producer.py
import os, sys, json, subprocess, shlex, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
TOOLS = ROOT / "tools"

def run(cmd, cwd=None, shell=False):
    print(f"[run] {cmd}")
    if shell and isinstance(cmd, str):
        r = subprocess.run(cmd, shell=True, cwd=cwd, check=True)
    else:
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        r = subprocess.run(cmd, cwd=cwd, check=True)
    return r

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tema", required=True)
    ap.add_argument("--foco", default="YouTube Short + LinkedIn")
    ap.add_argument("--brand", default="Spark Pro")
    ap.add_argument("--style", default="Clean tech, minimal, depth of field, no text")
    ap.add_argument("--voice", default="alloy")
    ap.add_argument("--min_scenes", type=int, default=6)
    ap.add_argument("--outdir", default="dist")
    args = ap.parse_args()

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    out_base = ROOT / args.outdir / date_str
    out_base.mkdir(parents=True, exist_ok=True)

    # 1) Generate content pack
    run([sys.executable, str(SCRIPTS / "generate_pack.py"),
         "--tema", args.tema,
         "--foco", args.foco,
         "--outdir", str(out_base)])

    short_script = out_base / "ShortScript.md"
    srt_in = out_base / "ShortSRT.srt"
    srt_synced = out_base / "ShortSRT_synced.srt"
    yt_desc = out_base / "YouTubeDesc.md"
    linkedin_post = out_base / "LinkedInPost.md"

    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    narration = assets / "narration.mp3"
    bg = assets / "bg.png"
    thumbnail = assets / "thumbnail.png"
    slides_dir = assets / "slides"
    slides_dir.mkdir(exist_ok=True)

    # 2) TTS
    run([sys.executable, str(TOOLS / "tts_narrate.py"),
         "--script", str(short_script),
         "--out", str(narration),
         "--voice", args.voice])

    # 2.1) BG fallback
    run([sys.executable, str(TOOLS / "make_bg.py"),
         "--out", str(bg)])

    # 3) Retime SRT
    run([sys.executable, str(TOOLS / "retime_srt.py"),
         "--srt", str(srt_in),
         "--audio", str(narration),
         "--out", str(srt_synced),
         "--method", "scale"])

    # 4) Storyboard slides
    run([sys.executable, str(TOOLS / "generate_storyboard.py"),
         "--script", str(short_script),
         "--outdir", str(slides_dir),
         "--style", args.style,
         "--brand", args.brand,
         "--min_scenes", str(args.min_scenes)])

    # 5) Render short from slides
    short_out = assets / "short_from_slides.mp4"
    run([str(TOOLS / "make_short_from_slides.sh"),
         "--slides_dir", str(slides_dir),
         "--audio", str(narration),
         "--srt", str(srt_synced),
         "--out", str(short_out)], shell=False)

    # 6) Thumbnail
    title_for_thumb = "AGENTE EM 1 NOITE"
    subtitle_for_thumb = f"{args.brand} | Spark Pro"
    run([sys.executable, str(TOOLS / "make_thumbnail.py"),
         "--title", title_for_thumb,
         "--subtitle", subtitle_for_thumb,
         "--out", str(thumbnail)])

    # 7) Metadata
    meta = {
        "tema": args.tema,
        "foco": args.foco,
        "brand": args.brand,
        "style": args.style,
        "date": date_str,
        "paths": {
            "short_script": str(short_script),
            "srt_synced": str(srt_synced),
            "narration": str(narration),
            "slides_dir": str(slides_dir),
            "video": str(short_out),
            "thumbnail": str(thumbnail),
            "youtube_desc": str(yt_desc),
            "linkedin_post": str(linkedin_post),
        },
        "upload_ready": True
    }
    (out_base / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[ok] Pipeline concluído. Arquivos prontos em {out_base} e assets/.")

if __name__ == "__main__":
    main()
