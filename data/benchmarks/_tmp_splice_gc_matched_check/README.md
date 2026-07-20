# Splice Sites All gc_matched

Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.
Task: 3-class splice-site classification.
match_mode=gc_matched
gc_bins=20
match_kmer=3
train_shared_overlap_per_label=7537
test_shared_overlap_per_label=780
train_selected_signature_total=36
test_selected_signature_total=10
train_gc_mean=label0=0.4437, label1=0.4449, label2=0.4428
val_gc_mean=label0=0.5162, label1=0.5279, label2=0.5279
test_gc_mean=label0=0.4277, label1=0.4317, label2=0.4320
train_signature_preview=(8,):21, (7,):15, (6,):15, (10,):15, (11,):12, (9,):12
test_signature_preview=(8,):9, (7,):9, (9,):3, (11,):3, (10,):3, (6,):3

train=90 counts={'0': 30, '1': 30, '2': 30}
val=18 counts={'0': 6, '1': 6, '2': 6}
test=30 counts={'0': 10, '1': 10, '2': 10}
