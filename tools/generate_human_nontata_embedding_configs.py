import copy
from pathlib import Path

import yaml


GRID = [
    {"tag": "emb_tw8_t10_s015", "token_window": 8, "top_ratio": 0.10, "score_scale": 0.15},
    {"tag": "emb_tw16_t10_s015", "token_window": 16, "top_ratio": 0.10, "score_scale": 0.15},
    {"tag": "ctx_tw8_t10_s015", "token_window": 8, "top_ratio": 0.10, "score_scale": 0.15},
    {"tag": "ctx_tw16_t10_s015", "token_window": 16, "top_ratio": 0.10, "score_scale": 0.15},
]


def main():
    template_path = Path("configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_pilot.yaml")
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    for item in GRID:
        config = copy.deepcopy(template)
        split_dir = f"data/benchmarks/human_nontata_promoters_embedding_{item['tag']}"
        config["data"]["splits"] = {
            "train": f"{split_dir}/train.csv",
            "val": f"{split_dir}/val.csv",
            "test": f"{split_dir}/test.csv",
        }
        config["debug"]["output_subdir"] = f"debug_real_dnabert2_germ_bo_human_nontata_{item['tag']}"
        out_path = Path(f"configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_{item['tag']}.yaml")
        out_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
