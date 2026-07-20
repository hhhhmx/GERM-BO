import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

import torch
from torch.utils.data import Dataset

from src.data.mock_dataset import DNA_TO_ID, encode_sequence


def _normalize_sequence(sequence: str) -> str:
    normalized = sequence.strip().upper()
    if not normalized:
        raise ValueError("Encountered an empty sequence in the genomic dataset.")
    invalid = sorted({base for base in normalized if base not in DNA_TO_ID})
    if invalid:
        raise ValueError("Unsupported bases found in sequence: {0}".format(",".join(invalid)))
    return normalized


def _parse_label(raw_label):
    if isinstance(raw_label, int):
        return raw_label
    if isinstance(raw_label, str):
        stripped = raw_label.strip()
        if stripped.isdigit() or (stripped.startswith("-") and stripped[1:].isdigit()):
            return int(stripped)
    return raw_label


def _read_jsonl(path: Path) -> List[Dict]:
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as error:
                raise ValueError("Invalid JSONL in {0} at line {1}: {2}".format(path, line_number, error))
    return records


def _read_csv(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_records(path: Path) -> List[Dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(path)
    if suffix == ".jsonl":
        return _read_jsonl(path)
    raise ValueError("Unsupported split file format for {0}. Use .csv or .jsonl".format(path))


class GenomicSequenceDataset(Dataset):
    def __init__(
        self,
        split_path: str,
        split_name: str,
        seq_length: int,
        sequence_column: str = "sequence",
        label_column: str = "label",
        id_column: Optional[str] = "id",
        metadata_column: Optional[str] = "metadata",
        tokenizer=None,
        tokenizer_mode: str = "raw",
        label_to_id: Optional[Dict] = None,
    ):
        self.split_name = split_name
        self.seq_length = seq_length
        self.tokenizer = tokenizer
        self.sequence_column = sequence_column
        self.label_column = label_column
        self.id_column = id_column
        self.metadata_column = metadata_column
        path = Path(split_path)
        self.tokenizer_mode = tokenizer_mode
        if not path.exists():
            raise FileNotFoundError("Dataset split not found: {0}".format(path))
        raw_records = _read_records(path)
        if not raw_records:
            raise ValueError("Dataset split is empty: {0}".format(path))
        self.label_to_id = {} if label_to_id is None else dict(label_to_id)
        self.samples = []
        for index, record in enumerate(raw_records):
            if self.sequence_column not in record or self.label_column not in record:
                raise ValueError(
                    "Each record in {0} must contain '{1}' and '{2}'.".format(
                        path, self.sequence_column, self.label_column
                    )
                )
            sequence = _normalize_sequence(record[self.sequence_column])
            raw_label = _parse_label(record[self.label_column])
            if raw_label not in self.label_to_id:
                self.label_to_id[raw_label] = len(self.label_to_id)
            sample_id = (
                str(record.get(self.id_column))
                if self.id_column and record.get(self.id_column) not in (None, "")
                else "{0}-{1}".format(split_name, index)
            )
            metadata = record.get(self.metadata_column) if self.metadata_column else None
            self.samples.append(
                {
                    "sequence": sequence,
                    "label": self.label_to_id[raw_label],
                    "sample_id": sample_id,
                    "metadata": metadata,
                }
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[index]
        sequence = sample["sequence"]
        if self.tokenizer is None:
            trimmed = sequence[: self.seq_length]
            encoded = encode_sequence(trimmed)
            input_ids = torch.tensor(encoded, dtype=torch.long)
            attention_mask = torch.ones_like(input_ids)
            pad_token_id = 0
        else:
            sequence_for_tokenizer = sequence
            if self.tokenizer_mode == "char_space":
                sequence_for_tokenizer = " ".join(list(sequence))
        encoded = self.tokenizer(
            sequence_for_tokenizer,
            truncation=True,
            max_length=self.seq_length,
            padding=False,
            return_tensors="pt",
        )
        input_ids = encoded["input_ids"].squeeze(0).to(dtype=torch.long)
        if "attention_mask" in encoded:
            attention_mask = encoded["attention_mask"].squeeze(0).to(dtype=torch.long)
        else:
            attention_mask = torch.ones_like(input_ids)
        pad_token_id = self.tokenizer.pad_token_id
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": torch.tensor(sample["label"], dtype=torch.long),
            "sequence": sequence,
            "id": sample["sample_id"],
            "metadata": sample["metadata"],
            "pad_token_id": pad_token_id,
        }
