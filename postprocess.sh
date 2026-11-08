#!/bin/bash
# Trim silence, slow to navigation pace (0.85x, approved by ear),
# normalize loudness, encode ogg. Mirrors voice/gen_voice.sh processing.
set -e
IN=wavs
OUT=voice/ms/voice
mkdir -p "$OUT"
for w in "$IN"/*.wav; do
  base=$(basename "$w" .wav)
  ffmpeg -y -loglevel error -i "$w" -af \
    "silenceremove=start_periods=1:start_duration=0.1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_duration=0.1:start_threshold=-50dB,areverse,atempo=0.85,loudnorm=I=-16:TP=-1.5:LRA=11" \
    -c:a libvorbis -q:a 4 "$OUT/$base.ogg"
done
touch "$OUT/../.nomedia"
ls "$OUT" | wc -l
