# Splice Sites All kmer_balanced

Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.
Task: 3-class splice-site classification.
match_mode=kmer_balanced
gc_bins=20
match_kmer=3
train_shared_overlap_per_label=6792
test_shared_overlap_per_label=641
train_selected_signature_total=36
test_selected_signature_total=10
train_gc_mean=label0=0.4572, label1=0.4607, label2=0.4618
val_gc_mean=label0=0.5429, label1=0.5375, label2=0.5367
test_gc_mean=label0=0.4655, label1=0.4657, label2=0.4693
train_signature_preview=(7, 'TTT'):12, (8, 'AAA'):9, (6, 'TTT'):9, (9, 'TTT'):6, (12, 'CTG'):6, (10, 'GGG'):6, (10, 'CAG'):3, (9, 'GAA'):3, (9, 'GGG'):3, (6, 'AAA'):3
test_signature_preview=(8, 'TTT'):6, (13, 'GGG'):3, (7, 'TTT'):3, (7, 'AAA'):3, (12, 'GGG'):3, (9, 'AAA'):3, (5, 'TTT'):3, (11, 'CCC'):3, (9, 'TTT'):3

train=90 counts={'0': 30, '1': 30, '2': 30}
val=18 counts={'0': 6, '1': 6, '2': 6}
test=30 counts={'0': 10, '1': 10, '2': 10}
