from src.utils import list_sequences

sequences = list_sequences("p53")
print(f"Loaded {len(sequences)} sequences for p53\n")
for label, record in sequences.items():
    print(f"{label}: {len(record.seq)} amino acids")