#!/bin/bash
# Package ms_0.voice.zip the way OsmAnd expects it (see voice/gen_voice.sh):
# flat entries (ms_tts.js + *.ogg + .nomedia at zip root). The app extracts
# voice zips into voice/<lang>/, so nested paths would double-nest.
set -e
OUT=voice/ms/voice
cp ms_tts.js voice/ms/ms_tts.js
rm -rf flat && mkdir flat
cp "$OUT"/*.ogg voice/ms/ms_tts.js flat/
touch flat/.nomedia
rm -f ms_0.voice.zip
cd flat
echo "Voice Data Malay (ms)" | zip ../ms_0.voice.zip ms_tts.js -c
zip ../ms_0.voice.zip *.ogg .nomedia
ls -l ../ms_0.voice.zip
