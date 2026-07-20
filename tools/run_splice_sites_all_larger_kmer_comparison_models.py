import argparse
import csv
import json
import random
from itertools import product
from pathlib import Path

import torch


SEEDS = [45, 46, 47, 48, 49]
ALPHABET = "ACGT"
KMERS = ["".join(item) for item in product(ALPHABET, repeat=3)]
KMER_TO_ID = {kmer: index for index, kmer in enumerate(KMERS)}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-dir", default="data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_s3")
    parser.add_argument("--output-prefix", default="results/splice_sites_all_larger_kmer_comparison")
    return parser.parse_args()


def read_split(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    sequences = [row["sequence"].upper() for row in rows]
    labels = torch.tensor([int(row["label"]) for row in rows], dtype=torch.long)
    return sequences, labels


def kmer_counts(sequences):
    features = torch.zeros((len(sequences), len(KMERS)), dtype=torch.float32)
    for row_index, sequence in enumerate(sequences):
        total = 0
        for index in range(max(len(sequence) - 2, 0)):
            kmer = sequence[index : index + 3]
            kmer_index = KMER_TO_ID.get(kmer)
            if kmer_index is not None:
                features[row_index, kmer_index] += 1.0
                total += 1
        if total > 0:
            features[row_index] /= total
    return features


def standardize(train_x, val_x, test_x):
    mean = train_x.mean(dim=0, keepdim=True)
    std = train_x.std(dim=0, keepdim=True).clamp_min(1e-6)
    return (train_x - mean) / std, (val_x - mean) / std, (test_x - mean) / std


def metrics(labels, predictions):
    labels = labels.cpu()
    predictions = predictions.cpu()
    accuracy = float((labels == predictions).float().mean().item())
    f1_values = []
    for label in sorted(labels.unique().tolist()):
        tp = int(((labels == label) & (predictions == label)).sum().item())
        fp = int(((labels != label) & (predictions == label)).sum().item())
        fn = int(((labels == label) & (predictions != label)).sum().item())
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1_values.append(2 * precision * recall / max(precision + recall, 1e-8))
    return {"accuracy": accuracy, "macro_f1": sum(f1_values) / max(len(f1_values), 1)}


def train_logreg(train_x, train_y, seed):
    torch.set_num_threads(4)
    torch.manual_seed(seed)
    model = torch.nn.Linear(train_x.shape[1], 3)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.05, weight_decay=0.01)
    criterion = torch.nn.CrossEntropyLoss()
    for _ in range(160):
        optimizer.zero_grad()
        loss = criterion(model(train_x), train_y)
        loss.backward()
        optimizer.step()
    return model


def train_linear_svm(train_x, train_y, seed):
    torch.set_num_threads(4)
    torch.manual_seed(seed)
    model = torch.nn.Linear(train_x.shape[1], 3)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.03, weight_decay=0.01)
    for _ in range(220):
        optimizer.zero_grad()
        scores = model(train_x)
        correct = scores.gather(1, train_y.view(-1, 1))
        margins = (scores - correct + 1.0).clamp_min(0.0)
        margins.scatter_(1, train_y.view(-1, 1), 0.0)
        loss = margins.mean()
        loss.backward()
        optimizer.step()
    return model


def predict_nb(train_x, train_y, test_x, alpha=1.0):
    class_log_prior = []
    feature_log_prob = []
    for label in range(3):
        group = train_x[train_y == label]
        class_log_prior.append(torch.log(torch.tensor((group.shape[0] + alpha) / (train_x.shape[0] + 3 * alpha))))
        counts = group.sum(dim=0) + alpha
        feature_log_prob.append(torch.log(counts / counts.sum()))
    class_log_prior = torch.stack(class_log_prior)
    feature_log_prob = torch.stack(feature_log_prob)
    return (test_x @ feature_log_prob.T + class_log_prior).argmax(dim=1)


def predict_centroid(train_x, train_y, test_x):
    centroids = []
    for label in range(3):
        centroid = train_x[train_y == label].mean(dim=0)
        centroids.append(centroid / centroid.norm().clamp_min(1e-6))
    centroids = torch.stack(centroids)
    normalized = test_x / test_x.norm(dim=1, keepdim=True).clamp_min(1e-6)
    return (normalized @ centroids.T).argmax(dim=1)


def evaluate_model(method, train_x, train_y, val_x, val_y, test_x, test_y, seed):
    if method == "kmer_logreg":
        model = train_logreg(train_x, train_y, seed)
        val_pred = model(val_x).argmax(dim=1)
        test_pred = model(test_x).argmax(dim=1)
    elif method == "kmer_linear_svm":
        model = train_linear_svm(train_x, train_y, seed)
        val_pred = model(val_x).argmax(dim=1)
        test_pred = model(test_x).argmax(dim=1)
    elif method == "kmer_multinomial_nb":
        val_pred = predict_nb(train_x.clamp_min(0.0), train_y, val_x.clamp_min(0.0))
        test_pred = predict_nb(train_x.clamp_min(0.0), train_y, test_x.clamp_min(0.0))
    elif method == "kmer_nearest_centroid":
        val_pred = predict_centroid(train_x, train_y, val_x)
        test_pred = predict_centroid(train_x, train_y, test_x)
    else:
        raise ValueError(method)
    val = metrics(val_y, val_pred)
    test = metrics(test_y, test_pred)
    return {
        "val_accuracy": val["accuracy"],
        "val_macro_f1": val["macro_f1"],
        "test_accuracy": test["accuracy"],
        "test_macro_f1": test["macro_f1"],
    }


def mean(values):
    return sum(values) / max(len(values), 1)


def std(values):
    if len(values) <= 1:
        return 0.0
    m = mean(values)
    return (sum((value - m) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    split_dir = Path(args.split_dir)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    train_seq, train_y = read_split(split_dir / "train.csv")
    val_seq, val_y = read_split(split_dir / "val.csv")
    test_seq, test_y = read_split(split_dir / "test.csv")
    train_counts = kmer_counts(train_seq)
    val_counts = kmer_counts(val_seq)
    test_counts = kmer_counts(test_seq)
    train_std, val_std, test_std = standardize(train_counts, val_counts, test_counts)

    specs = [
        ("kmer_logreg", "3-mer Logistic Regression", train_std, val_std, test_std),
        ("kmer_linear_svm", "3-mer Linear SVM", train_std, val_std, test_std),
        ("kmer_multinomial_nb", "3-mer Multinomial NB", train_counts, val_counts, test_counts),
        ("kmer_nearest_centroid", "3-mer Nearest Centroid", train_std, val_std, test_std),
    ]

    rows = []
    for seed in SEEDS:
        for method, label, train_x, val_x, test_x in specs:
            result = evaluate_model(method, train_x, train_y, val_x, val_y, test_x, test_y, seed)
            row = {
                "benchmark": "splice_sites_all_larger",
                "method": method,
                "label": label,
                "family": "traditional_kmer",
                "seed": seed,
                **result,
            }
            rows.append(row)
            print(json.dumps(row, sort_keys=True))

    summary = []
    for method, label, *_ in specs:
        group = [row for row in rows if row["method"] == method]
        acc = [row["test_accuracy"] for row in group]
        f1 = [row["test_macro_f1"] for row in group]
        summary.append(
            {
                "benchmark": "splice_sites_all_larger",
                "method": method,
                "label": label,
                "family": "traditional_kmer",
                "n_seeds": len(group),
                "test_accuracy_mean": mean(acc),
                "test_accuracy_std": std(acc),
                "test_macro_f1_mean": mean(f1),
                "test_macro_f1_std": std(f1),
                "per_seed_accuracy": " / ".join(f"{value:.4f}" for value in acc),
                "per_seed_macro_f1": " / ".join(f"{value:.4f}" for value in f1),
            }
        )

    write_csv(output_prefix.with_suffix(".csv"), rows)
    write_csv(Path(str(output_prefix) + "_summary.csv"), summary)
    md_path = output_prefix.with_suffix(".md")
    with md_path.open("w", encoding="utf-8") as handle:
        handle.write("# Splice Sites All Larger Split Traditional 3-mer Comparison Models\n\n")
        handle.write("Protocol: same `9000/1800/3000` split, seeds `45-49`, sequence-only 3-mer baselines.\n\n")
        handle.write("| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |\n")
        handle.write("|---|---:|---:|---:|---|\n")
        for row in summary:
            handle.write(
                f"| {row['label']} | {row['n_seeds']} | "
                f"{row['test_accuracy_mean']:.4f} +/- {row['test_accuracy_std']:.4f} | "
                f"{row['test_macro_f1_mean']:.4f} +/- {row['test_macro_f1_std']:.4f} | "
                f"{row['per_seed_accuracy']} |\n"
            )
    print(md_path)


if __name__ == "__main__":
    main()
