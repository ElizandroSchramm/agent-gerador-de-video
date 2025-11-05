#!/usr/bin/env bash
# tools/make_short.sh
# Renderiza um short vertical 1080x1920 com BG, SRT e narração.
# Requisitos: ffmpeg instalado.
# Uso:
#   bash tools/make_short.sh \
#     --bg assets/bg.png \
#     --srt dist/$(date +%F)/ShortSRT.srt \
#     --audio assets/narration.mp3 \
#     --out assets/short.mp4

set -e

while [[ $# -gt 0 ]]; do
  case $1 in
    --bg) BG="$2"; shift 2;;
    --srt) SRT="$2"; shift 2;;
    --audio) AUDIO="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "arg desconhecido: $1"; exit 1;;
  esac
done

if [[ -z "$BG" || -z "$SRT" || -z "$AUDIO" || -z "$OUT" ]]; then
  echo "Uso: --bg <bg.png> --srt <sub.srt> --audio <narration.mp3> --out <short.mp4>"
  exit 1
fi

# Cria um loop do BG (imagem estática) em 30fps e que dura o mesmo da narração
DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO")
ffmpeg -y -loop 1 -i "$BG" -i "$AUDIO" -t "$DUR" -r 30 -vf "scale=1080:1920,format=yuv420p,subtitles='${SRT//:/\\:}'" -c:v h264 -c:a aac -b:a 192k -shortest "$OUT"

echo "[ok] Vídeo gerado em $OUT"
