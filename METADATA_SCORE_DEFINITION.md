# Metadata Border Score Definition

This document defines the metadata score used by metadata-driven GERM-BO. The score is always a scalar stored in each sample's `metadata` field as:

```text
border_score=<float>
```

During batching, `src/utils/train_utils.py::parse_border_score` extracts this value and passes it to GERM-BO as `batch["border_scores"]`. In metadata-driven GERM-BO, the adapter uses `border_score_type: metadata_border_score`; the score modulates only the LoRA update branch, not the frozen backbone output.

## 1. How GERM-BO Uses The Score

For a sample or token with metadata score `s`, GERM-BO first normalizes the score within the current batch:

```text
s_norm = s / mean_batch(s)
```

The LoRA update is then scaled by:

```text
c = clip(1 + lambda * (s_norm - 1), c_min, c_max)
```

where the final main configuration uses:

```text
lambda = 0.27
c_min = 0.73
c_max = 1.42
```

The final adapted linear layer is:

```text
y = W x + scale * B(A(dropout(x)) * c)
```

For sequence-shaped hidden states, the same sample-level score is expanded to valid tokens using `attention_mask`.

## 2. Controlled Border-Aware Task Score

The main controlled experiments use synthetic/file-based border-aware splits where each sample has known motif/border construction metadata. The controlled metadata score is generated during split construction and written directly into the CSV metadata field.

Conceptually:

```text
border_score = normalized motif/border difficulty score
```

The score is aligned with the sample's constructed boundary difficulty. It is not the class label, but it is produced by the task generator, so it should be described as a controlled-task annotation rather than a naturally available biological annotation.

This is the setting where metadata-driven GERM-BO is strongest:

```text
hard_border_large, 13 seeds:
Baseline LoRA:              0.8377 +/- 0.0544 accuracy
Metadata-driven GERM-BO:    0.9519 +/- 0.0443 accuracy
```

Leakage control:

```text
metadata shuffled within each split
sequence unchanged
label unchanged
metadata-to-sample alignment broken
```

Shuffling removes the gain, supporting the claim that sample-to-border-score alignment matters.

## 3. Label-Free k-mer JSD Score

For real external benchmarks where no ground-truth border annotation is available, we estimate a label-free score from sequence content only.

Implementation:

```text
tools/prepare_genomic_benchmark.py
```

For a DNA sequence `x_1...x_L`, a candidate boundary at position `i`, window size `w`, and k-mer size `k`:

```text
left_i  = x[i-w : i]
right_i = x[i : i+w]
P_i     = k-mer distribution(left_i)
Q_i     = k-mer distribution(right_i)
raw_i   = JSD(P_i, Q_i)
```

The sequence-level raw score is the mean of the top `top_ratio` boundary scores:

```text
raw_sequence = mean(top raw_i values)
```

It is mapped to the GERM-BO score scale as:

```text
border_score = clip(score_base + score_scale * raw_sequence, score_min, score_max)
```

Default/current grid values:

```text
score_base = 0.75
score_min  = 0.60
score_max  = 1.50
```

Best first-stage k-mer candidate:

```text
window = 64
kmer = 2
top_ratio = 0.10
score_scale = 3.0
```

Important constraint:

```text
label is never read when computing this score
```

Current status:

```text
3-seed pilot: positive
held-out seeds 45-49: not stable
decision: promising but not promoted
```

## 4. Pretrained Representation-Shift Score

We also estimate a label-free score from frozen DNABERT-2 representations.

Implementation:

```text
tools/prepare_embedding_boundary_scores.py
```

For each sequence, DNABERT-2 tokenizes the DNA sequence and produces token representations `h_1...h_T`. For a candidate boundary `i` and token window `w`:

```text
left_i  = mean(h[i-w : i])
right_i = mean(h[i : i+w])
raw_i   = 1 - cosine(left_i, right_i)
```

The sequence-level raw score is:

```text
raw_sequence = mean(top raw_i values)
```

Scores are normalized using train-split statistics only:

```text
z = (raw_sequence - mean_train(raw)) / std_train(raw)
border_score = clip(1 + score_scale * z, score_min, score_max)
```

This avoids using validation/test distribution statistics and avoids labels.

Two representation sources are supported:

```text
token_embedding: frozen DNABERT-2 token embedding matrix only
contextual: frozen DNABERT-2 contextual hidden states
```

For contextual extraction, DNABERT-2 is forced onto its ordinary PyTorch attention path during score preparation by setting:

```text
attention_probs_dropout_prob = 0.1
```

This avoids the remote Triton/flash-attention compilation path. The model remains frozen; this is score extraction only.

Best current contextual candidate:

```text
ctx_tw16_t10_s015
token_window = 16
top_ratio = 0.10
score_scale = 0.15
```

Current status:

```text
seeds 42-44:
Baseline LoRA:                 0.8103 +/- 0.0021 accuracy
Contextual DNABERT-2 tw16:     0.8130 +/- 0.0040 accuracy
paired accuracy delta:         +0.0027
win rate:                      100%

decision: promising, but requires held-out seeds confirmation before promotion
```

## 5. What The Score Is Not

The metadata score is not:

```text
not the class label
not a predicted label probability
not computed from test labels
not tuned on test accuracy
not an extra input token to the backbone
```

The score is:

```text
a scalar side-channel used only to scale the GERM-BO adapter update
computed before training
fixed during training and evaluation
sample-aligned through metadata
```

## 6. Reporting Recommendation

Use this terminology in the paper:

```text
Controlled metadata score:
  Known border/difficulty annotation from the controlled border-aware task generator.

Label-free estimated score:
  Sequence-only score estimated from k-mer distribution shifts or frozen pretrained representation shifts.

Metadata-driven GERM-BO:
  GERM-BO using an explicit per-sample border score from metadata.

Metadata-estimated GERM-BO:
  GERM-BO using a label-free estimated border score on external benchmarks.
```

Recommended claim boundary:

```text
The controlled-task results demonstrate that GERM-BO benefits strongly when meaningful border scores are available.
External benchmark pilots show that estimating such scores from natural sequences is the current bottleneck.
```

## 7. Oracle vs Non-Oracle Interpretation

A potential concern is that the controlled-task metadata score is a synthetic oracle signal because it is produced by the task generator. We therefore separate three settings.

### Controlled Setting: Known Border Score

In the controlled border-aware splits, the generator knows the planted border or motif-boundary construction and writes a corresponding `border_score` into metadata. This score is not the label, but it is privileged controlled-task information.

This setting should be reported as:

```text
controlled / oracle-border-score setting
mechanism upper-bound test
```

It answers:

```text
If a meaningful border score is available, can GERM-BO exploit it?
```

Current answer:

```text
Yes. Metadata-driven GERM-BO substantially improves over Baseline LoRA and activation-derived GERM-BO on the controlled hard-border task.
```

It should not be reported as:

```text
evidence that natural biological datasets automatically provide usable border scores
```

### Shuffled Ablation: Metadata Channel Leakage Control

The shuffled metadata ablation keeps:

```text
sequence unchanged
label unchanged
training/evaluation protocol unchanged
metadata format unchanged
```

but breaks:

```text
sample-to-border-score alignment
```

This setting answers:

```text
Is the gain caused by a generic metadata side channel or accidental label leakage?
```

Current answer:

```text
No. Shuffling metadata removes the gain, and shuffled metadata performs below real metadata.
```

This does not prove that the controlled score is naturally available; it proves that the controlled-task gain depends on correct score alignment rather than metadata presence alone.

### External Pilot: Non-Oracle Estimated Score

For real genomic benchmarks, ground-truth border annotations are not provided. We therefore estimate `border_score` from sequence only:

```text
k-mer Jensen-Shannon boundary shift
frozen/contextual DNABERT-2 representation shift
```

These scores are non-oracle:

```text
no label input
no test-label input
computed before training
fixed during training/evaluation
```

This setting answers:

```text
Can we recover useful border scores from natural sequences without annotations?
```

Current answer:

```text
Only partially. Simple k-mer JSD is unstable on held-out seeds. Contextual DNABERT-2 tw16 is promising in a 3-seed pilot but still needs held-out confirmation.
```

Recommended paper framing:

```text
The controlled setting validates the GERM-BO mechanism under known border scores.
The shuffled ablation rules out metadata-channel leakage in the controlled setting.
The external pilot evaluates the harder non-oracle problem of estimating border scores from natural sequences.
```

## 8. Claim Boundary Table

| Claim | Status | Evidence | Caveat |
|---|---|---|---|
| Controlled mechanism works strongly | Supported | Metadata-driven GERM-BO strongly improves over Baseline LoRA on controlled `hard_border_large`. | This uses known/oracle controlled border scores. |
| Not metadata leakage | Supported | Shuffled metadata ablation removes the gain while preserving sequence and label. | This controls metadata-channel leakage, not natural score availability. |
| External non-oracle estimator remains open | Supported as limitation | k-mer JSD and contextual DNABERT-2 estimators do not stably beat baseline on held-out seeds. | External benchmark is not the current main contribution. |
| Contextual estimator is promising but unconfirmed | Not promoted | Contextual `tw16` wins in seeds `42-44` but loses on held-out seeds `45-49`. | Treat as diagnostic/future-work direction only. |

Recommended one-sentence summary:

```text
GERM-BO works strongly when meaningful border scores are available; estimating such scores robustly in non-oracle real genomic benchmarks remains the key open problem.
```
