#!/usr/bin/env bash
# Download NT / HyenaDNA assets via hf-mirror (gpu-server).
set -euo pipefail

cd ~/germ_bo_project
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"

${PYTHON_BIN} - <<'PY'
from huggingface_hub import snapshot_download

downloads = [
    ("InstaDeepAI/nucleotide-transformer-v2-50m-multi-species", "local_assets/nt_v2_50m"),
    ("LongSafari/hyenadna-tiny-1k-seqlen-hf", "local_assets/hyenadna_tiny_1k_hf"),
]
for repo, local in downloads:
    print("downloading", repo, "->", local)
    snapshot_download(repo, local_dir=local)
    print("done", local)
PY
