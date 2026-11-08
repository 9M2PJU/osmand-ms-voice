#!/bin/bash
# Package ms_0.voice.zip the way OsmAnd expects it (see voice/gen_voice.sh):
# ms_tts.js + *.ogg + .nomedia. ms_tts.js is copied from the TTS PR/content.
set -e
OUT=voice/ms/voice
cp ms_tts.js voice/ms/ms_tts.js
rm -f ms_0.voice.zip
echo "Voice Data Malay (ms)" | zip ms_0.voice.zip voice/ms/ms_tts.js -c
zip ms_0.voice.zip "$OUT"/*.ogg voice/ms/.nomedia
ls -l ms_0.voice.zip
