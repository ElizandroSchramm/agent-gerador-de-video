# scripts/generate_pack.py
# Requer: pip install agno openai python-dotenv
import os, argparse, re, textwrap
from pathlib import Path
from agents.spark_pro import render
# --- sys.path bootstrap (allows running this script directly) ---
import sys, pathlib
THIS_FILE = pathlib.Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent  # repo root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# ----------------------------------------------------------------

def split_sections(full: str):
    # Split by headers like "# FileName"
    parts = re.split(r"(?m)^#\s+([A-Za-z0-9_.-]+)\s*$", full)
    # parts -> ["preamble", "File1", "content1", "File2", "content2", ...]
    bundled = {}
    if len(parts) > 1:
        preamble = parts[0]
        for i in range(1, len(parts), 2):
            name = parts[i].strip()
            content = parts[i+1].strip()
            bundled[name] = content
    else:
        bundled["Output.md"] = full
    return bundled

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tema", required=True, help="Tema do conteúdo")
    ap.add_argument("--foco", default="", help="Foco opcional")
    ap.add_argument("--outdir", default="dist", help="Diretório de saída")
    args = ap.parse_args()

    result = render(args.tema, args.foco or None)
    files = split_sections(result)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for name, content in files.items():
        (outdir / name).write_text(content, encoding="utf-8")

    print(f"Gerado {len(files)} arquivos em {outdir.resolve()}")

if __name__ == "__main__":
    main()