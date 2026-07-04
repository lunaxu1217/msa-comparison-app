from pathlib import Path
from Bio import SeqIO

DATA_DIR = Path(__file__).parent.parent / "data"

def list_proteins():
    """Return available protein folders, e.g. ['h3h4', 'hemoglobin', 'p53']"""
    return sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()])

def list_sequences(protein: str):
    """Return dict of {species_label: SeqRecord} for a given protein folder."""
    folder = DATA_DIR / protein
    records = {}
    for fasta_file in sorted(folder.glob("*.fasta")):
        record = SeqIO.read(fasta_file, "fasta")
        records[fasta_file.stem] = record
    return records