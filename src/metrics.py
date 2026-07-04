from collections import Counter

def alignment_length(aln):
    return aln.get_alignment_length()

def percent_conserved(aln):
    length = aln.get_alignment_length()
    conserved = 0
    for i in range(length):
        column = aln[:, i]
        if len(set(column)) == 1 and column[0] != "-":
            conserved += 1
    return round(100 * conserved / length, 2)

def percent_gaps(aln):
    total_chars = sum(len(record.seq) for record in aln)
    gap_chars = sum(str(record.seq).count("-") for record in aln)
    return round(100 * gap_chars / total_chars, 2)

def column_score(aln):
    length = aln.get_alignment_length()
    scores = []
    for i in range(length):
        column = aln[:, i]
        residues = [c for c in column if c != "-"]
        if len(residues) < 2:
            scores.append(0)
            continue
        counts = Counter(residues)
        matches = sum(c * (c - 1) / 2 for c in counts.values())
        total_pairs = len(residues) * (len(residues) - 1) / 2
        scores.append(matches / total_pairs if total_pairs else 0)
    return round(100 * sum(scores) / length, 2)

def compute_all_metrics(aln):
    return {
        "Alignment Length": alignment_length(aln),
        "% Conserved Positions": percent_conserved(aln),
        "% Gaps": percent_gaps(aln),
        "Column Score": column_score(aln),
    }