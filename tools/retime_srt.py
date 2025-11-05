# tools/retime_srt.py
import argparse, subprocess, re, sys
TS = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")
def parse_ts(s):
    h, m, sec, ms = map(int, TS.match(s).groups())
    return h*3600 + m*60 + sec + ms/1000.0
def fmt_ts(t):
    if t < 0: t = 0
    ms = int(round((t - int(t)) * 1000))
    s = int(t) % 60
    m = (int(t) // 60) % 60
    h = int(t) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def get_audio_duration(audio_path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", audio_path], text=True).strip()
    return float(out)
def read_srt(path):
    content = open(path, "r", encoding="utf-8").read()
    blocks = re.split(r"\n\s*\n", content.strip(), flags=re.M)
    entries = []
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) >= 2:
            idx = lines[0].strip()
            m = re.search(r"(\d\d:\d\d:\d\d,\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d,\d\d\d)", lines[1])
            if not m: continue
            start = parse_ts(m.group(1)); end = parse_ts(m.group(2))
            text = "\n".join(lines[2:])
            entries.append((idx, start, end, text))
    return entries
def write_srt(entries, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, (_, start, end, text) in enumerate(entries, 1):
            f.write(f"{i}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}\n\n")
    print(f"[ok] SRT salvo em {out_path}")
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--srt", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--method", choices=["scale","pad","trim"], default="scale")
    args = ap.parse_args()
    entries = read_srt(args.srt)
    srt_total = entries[-1][2]
    aud_total = get_audio_duration(args.audio)
    if args.method == "scale":
        k = aud_total / srt_total if srt_total > 0 else 1.0
        out = [(i, s*k, e*k, t) for i, s, e, t in entries]
    elif args.method == "pad":
        extra = max(0.0, aud_total - srt_total); gap = extra / len(entries)
        shift = 0.0; out = []
        for i, s, e, t in entries:
            out.append((i, s+shift, e+shift, t)); shift += gap
    else:
        out = []
        for i, s, e, t in entries:
            ne = min(e, aud_total)
            if s >= aud_total: break
            out.append((i, s, ne, t))
    write_srt(out, args.out)
if __name__ == "__main__":
    main()
