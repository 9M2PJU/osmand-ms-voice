"""Batch-synthesize the Malay OsmAnd recorded voice pack (CPU-friendly).

Usage:
  python synth.py [--speaker idayu] [--only left.ogg,meters.ogg]

Reads manifest.json (ogg filename -> Malay sentence), writes 24 kHz wavs
into wavs/. Skips files that already exist, so reruns resume.
Post-processing (trim/pace/normalize/ogg) is done by postprocess.sh.
"""

import argparse
import json
import os
import re
import sys
import time

import soundfile as sf
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from distilcodec import DistilCodec

ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT, "models")
WAVS_DIR = os.path.join(ROOT, "wavs")
MANIFEST = os.path.join(ROOT, "manifest.json")

torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))


def load_codec():
    from distilcodec import DistilCodec as DC

    with open(os.path.join(MODELS_DIR, "distilcodec", "model_config.json")) as f:
        config = json.load(f)
    codec = DC(config)
    codec.device = torch.device("cpu")
    state = DC.load_checkpoint(
        os.path.join(MODELS_DIR, "distilcodec", "g_00204000"), codec.device
    )
    codec.generator.load_state_dict(state["generator"])
    codec.encoder.load_state_dict(state["encoder"])
    codec.quantizer.load_state_dict(state["quantizer"])
    return codec.eval()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speaker", default="idayu")
    ap.add_argument("--only", default="")
    ap.add_argument("--shard", default="",
                    help="shard filter as INDEX/TOTAL, e.g. 2/5")
    args = ap.parse_args()

    print("loading codec...", flush=True)
    codec = load_codec()
    print("loading tokenizer + LM...", flush=True)
    qwen = os.path.join(MODELS_DIR, "qwen-tts")
    tokenizer = AutoTokenizer.from_pretrained(qwen)
    model = AutoModelForCausalLM.from_pretrained(
        qwen, torch_dtype=torch.float32, device_map="cpu"
    ).eval()

    manifest = json.load(open(MANIFEST))
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    items = [(k, v) for k, v in manifest.items() if not only or k in only]
    if args.shard:
        idx, total = (int(x) for x in args.shard.split("/"))
        items = [it for n, it in enumerate(items) if n % total == idx]
    os.makedirs(WAVS_DIR, exist_ok=True)

    for i, (fname, text) in enumerate(items):
        out = os.path.join(WAVS_DIR, fname.replace(".ogg", ".wav"))
        if os.path.exists(out):
            print("[%d/%d] %s exists, skipping" % (i + 1, len(items), fname), flush=True)
            continue
        t0 = time.time()
        prompt = "<|im_start|>%s: %s<|speech_start|>" % (args.speaker, text)
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        with torch.no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True,
                repetition_penalty=1.1,
            )
        tail = tokenizer.decode(gen[0]).split("<|speech_start|>")[-1]
        tail = tail.replace("<|endoftext|>", "")
        codes = list(map(int, re.findall(r"speech_(\d+)", tail)))
        if not codes:
            print("NO SPEECH TOKENS for %r, skipping" % text, flush=True)
            continue
        with torch.no_grad():
            y = codec.decode_from_codes(codes, minus_token_offset=False)
        wav = y[0, 0].cpu().numpy()
        sf.write(out, wav, 24000)
        print(
            "[%d/%d] %s <- %r (%.1fs audio, %.0fs wall)"
            % (i + 1, len(items), fname, text, len(wav) / 24000, time.time() - t0),
            flush=True,
        )


if __name__ == "__main__":
    main()
