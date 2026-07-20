# Splice Sites All gc_matched

Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.
Task: 3-class splice-site classification.
match_mode=gc_matched
gc_bins=20
match_kmer=3
train_shared_overlap_per_label=7537
test_shared_overlap_per_label=780
train_selected_signature_total=3600
test_selected_signature_total=600
train_gc_mean=label0=0.4561, label1=0.4569, label2=0.4561
val_gc_mean=label0=0.4485, label1=0.4472, label2=0.4483
test_gc_mean=label0=0.4539, label1=0.4561, label2=0.4549
train_signature_preview=(8,):1509, (7,):1389, (6,):1338, (9,):1305, (10,):1209, (11,):825, (12,):642, (5,):351, (13,):315, (14,):87
test_signature_preview=(8,):327, (7,):294, (9,):258, (6,):252, (10,):249, (11,):138, (12,):129, (13,):69, (5,):66, (14,):18

train=9000 counts={'0': 3000, '1': 3000, '2': 3000}
val=1800 counts={'0': 600, '1': 600, '2': 600}
test=1800 counts={'0': 600, '1': 600, '2': 600}
