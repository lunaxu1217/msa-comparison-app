import subprocess
import tempfile
from pathlib import Path
from Bio import SeqIO, AlignIO

def _write_temp_fasta(records: dict) -> Path:
    """Write a dict of {label: SeqRecord} to a temp FASTA file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False, mode="w")
    for label, record in records.items():
        record.id = label
        record.description = ""
        SeqIO.write(record, tmp, "fasta")
    tmp.close()
    return Path(tmp.name)

def run_muscle(records: dict):
    infile = _write_temp_fasta(records)
    outfile = infile.with_suffix(".aln.fasta")
    cmd = ["muscle", "-align", str(infile), "-output", str(outfile)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"MUSCLE failed: {result.stderr}")
    return AlignIO.read(outfile, "fasta")

def run_clustalo(records: dict):
    infile = _write_temp_fasta(records)
    outfile = infile.with_suffix(".aln.fasta")
    cmd = ["clustalo", "-i", str(infile), "-o", str(outfile), "--force", "--outfmt=fasta"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError(
            "Clustal Omega is not installed or not found on PATH. "
            "See README.md 'Known Limitations' section for Windows setup options."
        )
    if result.returncode != 0:
        raise RuntimeError(f"Clustal Omega failed: {result.stderr}")
    return AlignIO.read(outfile, "fasta")

def run_mafft(records: dict):
    infile = _write_temp_fasta(records)
    outfile = infile.with_suffix(".aln.fasta")
    cmd = ["mafft", "--auto", str(infile)]
    with open(outfile, "w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"MAFFT failed: {result.stderr}")
    return AlignIO.read(outfile, "fasta")

RUNNERS = {
    "MUSCLE": run_muscle,
    "Clustal Omega": run_clustalo,
    "MAFFT": run_mafft,
}