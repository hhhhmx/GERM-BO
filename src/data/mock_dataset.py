import random
from typing import Dict, List

import torch
from torch.utils.data import Dataset

from src.utils.border_features import normalized_border_length


DNA_TO_ID = {"A": 0, "C": 1, "G": 2, "T": 3}
BACKGROUND_PATTERNS = ("ACGT", "TGCA", "CATG", "GTAC")
HIGH_BORDER_MOTIF = "ATATAT"
LOW_BORDER_MOTIF = "ACGTGA"
SHARED_DISTRACTOR = "GCGT"


def encode_sequence(sequence: str) -> List[int]:
    return [DNA_TO_ID[base] for base in sequence]


def _seed_for_split(split: str) -> int:
    return {"train": 13, "val": 17, "test": 19}.get(split, 23)


def _fill_background(seq_length: int, rng: random.Random) -> List[str]:
    chars = []
    while len(chars) < seq_length:
        chars.extend(list(rng.choice(BACKGROUND_PATTERNS)))
    return chars[:seq_length]


def _insert_token(chars: List[str], token: str, start: int) -> None:
    end = min(start + len(token), len(chars))
    for offset, char in enumerate(token[: end - start]):
        chars[start + offset] = char


def _jitter_start(base_start: int, jitter: int, limit: int, rng: random.Random) -> int:
    return max(0, min(limit, base_start + rng.randint(-jitter, jitter)))


def _build_sequence(label: int, seq_length: int, rng: random.Random) -> Dict[str, object]:
    chars = _fill_background(seq_length, rng)
    motif = HIGH_BORDER_MOTIF if label == 1 else LOW_BORDER_MOTIF
    repeats = 3 if label == 1 else 1
    center = seq_length // 2 - len(motif)
    burst_positions = []
    for repeat in range(repeats):
        start = _jitter_start(center + repeat * 2, jitter=1, limit=seq_length - len(motif), rng=rng)
        _insert_token(chars, motif, start)
        burst_positions.append(start)

    distractor_count = 3 if label == 0 else 1
    for distractor_index in range(distractor_count):
        start = _jitter_start(
            base_start=(distractor_index * 7 + 3) % max(seq_length - len(SHARED_DISTRACTOR), 1),
            jitter=2,
            limit=seq_length - len(SHARED_DISTRACTOR),
            rng=rng,
        )
        _insert_token(chars, SHARED_DISTRACTOR, start)

    sequence = "".join(chars)
    return {
        "sequence": sequence,
        "motif": motif,
        "motif_repeats": repeats,
        "motif_border_score": normalized_border_length(motif),
        "burst_positions": burst_positions,
    }


class MockGenomicDataset(Dataset):
    def __init__(self, size: int, seq_length: int, split: str):
        rng = random.Random(1000 + _seed_for_split(split) + size * 31 + seq_length * 7)
        self.samples = []
        for index in range(size):
            label = index % 2
            built = _build_sequence(label=label, seq_length=seq_length, rng=rng)
            self.samples.append(
                {
                    "sequence": built["sequence"],
                    "label": label,
                    "sample_id": "{0}-{1}".format(split, index),
                    "metadata": {
                        "task": "border_burst_classification",
                        "motif": built["motif"],
                        "motif_repeats": built["motif_repeats"],
                        "motif_border_score": built["motif_border_score"],
                        "burst_positions": built["burst_positions"],
                    },
                }
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[index]
        input_ids = torch.tensor(encode_sequence(sample["sequence"]), dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": torch.tensor(sample["label"], dtype=torch.long),
            "sequence": sample["sequence"],
            "id": sample["sample_id"],
            "metadata": sample["metadata"],
            "pad_token_id": 0,
        }
