"""Make the pip-installed DistilCodec runnable on CPU-only machines.

Upstream hardcodes cuda:0 in from_pretrained/move_to_cuda/decode paths.
We avoid from_pretrained entirely (see synth.py) and only need this one
tensor-creation site neutralized for CPU decode.
"""
import site
import glob
import os

paths = glob.glob(
    os.path.join(site.getsitepackages()[0], "distilcodec", "distil_codec.py")
)
assert paths, "distilcodec not installed"
path = paths[0]
src = open(path).read()
old = ".unsqueeze(-1).cuda()"
assert src.count(old) == 1, "unexpected distil_codec.py layout"
src = src.replace(old, ".unsqueeze(-1)")
old_amp = 'torch.autocast(device_type="cuda"'
if old_amp in src:
    src = src.replace(old_amp, 'torch.autocast(device_type="cpu"')
open(path, "w").write(src)
print("patched", path, "for CPU")
