#!/usr/bin/env bash
set -e

while [[ $# -gt 0 ]]; do
  case $1 in
    --slides_dir) SLIDES="$2"; shift 2;;
    --audio) AUDIO="$2"; shift 2;;
    --srt) SRT="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "arg desconhecido: $1"; exit 1;;
  esac
done

if [[ -z "$SLIDES" || -z "$AUDIO" || -z "$SRT" || -z "$OUT" ]]; then
  echo "Uso: --slides_dir <dir> --audio <narration.mp3> --srt <legendas.srt> --out <out.mp4>"
  exit 1
fi

# Normaliza caminhos ABSOLUTOS (sem heredoc; compatível com bash do macOS)
SLIDES="$(cd "$SLIDES" && pwd)"
AUDIO="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$AUDIO")"
SRT="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$SRT")"
OUT_DIR="$(dirname "$OUT")"
mkdir -p "$OUT_DIR"

# Duração do áudio
DUR="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO")"

# Contagem de slides (NÃO use ls; use glob com aspas)
COUNT=0
for f in "$SLIDES"/slide_*.png; do
  [[ -e "$f" ]] || continue
  COUNT=$((COUNT+1))
done
if [[ "$COUNT" -eq 0 ]]; then
  echo "Nenhum slide encontrado em $SLIDES"; exit 1
fi

# Caso especial: apenas 1 slide -> loop
if [[ "$COUNT" -eq 1 ]]; then
  for ONE in "$SLIDES"/slide_*.png; do break; done
  ffmpeg -y -loop 1 -i "$ONE" -i "$AUDIO" -t "$DUR" \
    -vf "scale=1024x1536,format=yuv420p,subtitles='${SRT//:/\\:}'" \
    -r 30 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT"
  echo "[ok] Vídeo gerado em $OUT (1 slide, loop)"
  exit 0
fi

# Duração por slide
PER="$(python3 -c "print(float('$DUR')/float('$COUNT'))")"

# Lista de concat com caminhos ABSOLUTOS e ASPAS
LIST="$(mktemp)"
for f in "$SLIDES"/slide_*.png; do
  [[ -e "$f" ]] || continue
  ABS="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$f")"
  printf "file '%s'\n" "$ABS" >> "$LIST"
  printf "duration %s\n" "$PER" >> "$LIST"
done
# repete o último para evitar corte abrupto
LAST=""
for f in "$SLIDES"/slide_*.png; do LAST="$f"; done
ABS_LAST="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$LAST")"
printf "file '%s'\n" "$ABS_LAST" >> "$LIST"

# Render com zoom leve + legendas (escapa dois-pontos na path do SRT)
ffmpeg -y -f concat -safe 0 -i "$LIST" -i "$AUDIO" \
  -vf "scale=1024x1536,zoompan=d=125:s=1024x1536,format=yuv420p,subtitles='${SRT//:/\\:}'" \
  -r 30 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT"

rm -f "$LIST"
echo "[ok] Vídeo gerado em $OUT"