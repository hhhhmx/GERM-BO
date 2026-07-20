import copy
from pathlib import Path

import yaml


GRID = [
    {"tag": "w16_k2_t10_s3", "window": 16, "kmer": 2, "top_ratio": 0.10, "score_scale": 3.0},
    {"tag": "w32_k2_t10_s3", "window": 32, "kmer": 2, "top_ratio": 0.10, "score_scale": 3.0},
    {"tag": "w64_k2_t10_s3", "window": 64, "kmer": 2, "top_ratio": 0.10, "score_scale": 3.0},
    {"tag": "w32_k3_t10_s3", "window": 32, "kmer": 3, "top_ratio": 0.10, "score_scale": 3.0},
    {"tag": "w32_k2_t20_s3", "window": 32, "kmer": 2, "top_ratio": 0.20, "score_scale": 3.0},
    {"tag": "w32_k2_t10_s6", "window": 32, "kmer": 2, "top_ratio": 0.10, "score_scale": 6.0},
]


def main():
    template_path = Path("configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_pilot.yaml")
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    for item in GRID:
        config = copy.deepcopy(template)
        split_dir = f"data/benchmarks/human_nontata_promoters_border_estimated_{item['tag']}"
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
