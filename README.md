# Spark Pro — Agente Multimodal (MVP)

Este pacote cria um **agente multimodal** para transformar um **tema de IA** em um **kit de conteúdo**.

## O que vem pronto
- Prompt de sistema robusto do agente (`prompts/spark_pro_system.md`)
- Agente em Python com **Agno + OpenAI** (`agents/spark_pro.py`)
- CLI para gerar o pacote de arquivos (`scripts/generate_pack.py`)

## Requisitos
```bash
python3 -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install agno openai python-dotenv
echo "OPENAI_API_KEY=xxx" > .env
# opcional:
echo "OPENAI_MODEL=gpt-4o-mini" >> .env
echo "OPENAI_MODEL_FAST=gpt-4o-mini" >> .env
```

## Gerar o pacote multimodal (roteiro, SRT, posts, etc.)
```bash
python3 -m scripts.generate_pack --tema "SEU TEMA AQUI" --foco "YouTube Short + LinkedIn" --outdir dist/$(date +%F)
```

Os arquivos serão gerados em `dist/<data>/` com:
- `ShortScript.md`, `ShortSRT.srt`, `YouTubeDesc.md`, `LinkedInPost.md`,
- `LongOutline.md`, `ThumbnailBrief.md`, `BrollList.md`, `Hooks.md`, `CTA.md`

## Gerar narração (TTS) a partir do roteiro
```bash
python3 tools/tts_narrate.py --script dist/$(date +%F)/ShortScript.md --out assets/narration.mp3 --voice alloy
```

O arquivo será gerado em `assets/narration.mp3.

## Sincronizar a SRT com a duração do áudio (corrige legenda acelerada/lenta)
```bash
python3 tools/retime_srt.py --srt dist/$(date +%F)/ShortSRT.srt --audio assets/narration.mp3 --out dist/$(date +%F)/ShortSRT_synced.srt --method scale
```

O arquivo ShortSRT_synced.srt será gerado em dist/<data>.

## Gerar as imagens (storyboard) com LLM
```bash
python3 tools/generate_storyboard.py --script dist/$(date +%F)/ShortScript.md --outdir assets/slides --style "Clean tech, minimal, depth of field, no text" --brand "SUA MARCA" --min_scenes 6
```

## Renderizar o Short com slides + legendas + narração
```bash
bash tools/make_short_from_slides.sh --slides_dir assets/slides --audio assets/narration.mp3 --srt dist/$(date +%F)/ShortSRT_synced.srt --out assets/short_from_slides.mp4
```

## (Opcional) Gerar thumbnail
```bash
python3 tools/make_thumbnail.py --title "SEU TEMA" --subtitle "UM SUBTITULO SEU" --out assets/thumbnail.png
```

## Para fazer tudo de uma vez sem rodar os passos anteriores
```bash
python3 run_producer.py --tema "SEU TEMA" --foco "YouTube Short + LinkedIn" --brand SUA_MARCA --style "Clean tech, minimal, depth of field, no text" --voice alloy --min_scenes 6 --outdir dist
```