# OsmAnd Malay recorded voice factory

Generates the 125-clip Malay (ms) recorded voice pack for OsmAnd navigation
(`ms_0.voice.zip`) on GitHub Actions CPU runners — no local GPU needed.

Voice: **idayu** from `mesolitica/Malaysian-TTS-0.6B-v1` (open source,
Malaysian lab). Phrasing: `ms_tts.js` (same content as the TTS voice).
**All audio in this pack is AI-synthesized** (required announcement per the
StyleTTS2/model terms; no real speaker's voice is cloned).

Run: Actions tab → "Generate Malay recorded voice" → Run workflow.
Reruns resume (wavs + models are cached). Output: `ms_voice-pack` artifact
with `ms_0.voice.zip` + all `*.ogg`.

Attribution: Mesolitica (TTS models), IDEA-Emdoor (DistilCodec),
Wikimedia Commons `Ms-kelentit-article.ogg` (CC BY-SA 3.0, style reference
used during development only — not shipped).
