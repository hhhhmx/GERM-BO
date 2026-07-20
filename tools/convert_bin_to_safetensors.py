from pathlib import Path
import sys

import torch
from safetensors.torch import save_file


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/convert_bin_to_safetensors.py <model_dir>")
    model_dir = Path(sys.argv[1]).resolve()
    source_path = model_dir / "pytorch_model.bin"
    target_path = model_dir / "model.safetensors"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source checkpoint: {source_path}")
    state_dict = torch.load(source_path, map_location="cpu")
    if not isinstance(state_dict, dict):
        raise TypeError("Expected a state_dict dictionary in pytorch_model.bin")
    tensor_state = {}
    seen_storage = {}
    for key, value in state_dict.items():
        if not torch.is_tensor(value):
            continue
        if key == "cls.predictions.decoder.weight" and "bert.embeddings.word_embeddings.weight" in state_dict:
            continue
        storage_key = (value.untyped_storage().data_ptr(), tuple(value.shape), str(value.dtype))
        if storage_key in seen_storage:
            continue
        seen_storage[storage_key] = key
        tensor_state[key] = value.contiguous()
    save_file(tensor_state, str(target_path))
    print(target_path.as_posix())


if __name__ == "__main__":
    main()
