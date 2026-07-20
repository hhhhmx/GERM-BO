# Splice Sites All kmer_balanced

Source: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`.
Task: 3-class splice-site classification.
match_mode=kmer_balanced
gc_bins=20
match_kmer=3
train_shared_overlap_per_label=6792
test_shared_overlap_per_label=641
train_selected_signature_total=3600
test_selected_signature_total=600
train_gc_mean=label0=0.4566, label1=0.4569, label2=0.4569
val_gc_mean=label0=0.4499, label1=0.4499, label2=0.4491
test_gc_mean=label0=0.4533, label1=0.4548, label2=0.4537
train_signature_preview=(7, 'TTT'):1104, (6, 'TTT'):870, (8, 'TTT'):822, (9, 'TTT'):378, (7, 'AAA'):318, (5, 'TTT'):297, (6, 'AAA'):267, (8, 'AAA'):243, (12, 'CCC'):216, (12, 'GGG'):177
test_signature_preview=(7, 'TTT'):213, (6, 'TTT'):189, (8, 'TTT'):177, (7, 'AAA'):99, (6, 'AAA'):93, (9, 'TTT'):81, (8, 'AAA'):66, (13, 'GGG'):48, (5, 'TTT'):45, (12, 'GGG'):39

train=9000 counts={'0': 3000, '1': 3000, '2': 3000}
val=1800 counts={'0': 600, '1': 600, '2': 600}
test=1800 counts={'0': 600, '1': 600, '2': 600}
