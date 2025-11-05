# tools/tts_narrate.py
# Usage:
#   python tools/tts_narrate.py --script 2025-11-04/ShortScript.md --out assets/narration.mp3 --voice alloy
# Requer: pip install -U openai python-dotenv
import argparse, os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Caminho do ShortScript.md")
    ap.add_argument("--out", default="assets/narration.mp3", help="Arquivo MP3 de saída")
    ap.add_argument("--voice", default="alloy", help="Voz TTS (ex.: alloy, verse, coral)")
    ap.add_argument("--model", default=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"), help="Modelo TTS")
    args = ap.parse_args()

    text = Path(args.script).read_text(encoding="utf-8")
    # Remove tags de seção do roteiro
    for tag in ["[GANCHO]", "[PARTE 1 — PROBLEMA]", "[PARTE 2 — PROPOSTA]", "[PARTE 3 — PASSOS PRÁTICOS]", "[CTA]"]:
        text = text.replace(tag, "")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # API atual: streaming para arquivo; usa response_format="mp3"
        with client.audio.speech.with_streaming_response.create(
            model=args.model,
            voice=args.voice,
            input=text.strip(),
            response_format="mp3",
        ) as response:
            response.stream_to_file(out_path)

        print(f"[ok] Narration gerada em {out_path}")
    except Exception as e:
        print(f"[erro] Falha ao sintetizar voz: {e}\n"
              f"Dicas: 'pip install -U openai' e garanta OPENAI_API_KEY no .env.")
        sys.exit(1)

if __name__ == "__main__":
    main()
