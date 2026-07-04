from src.utils import list_sequences
from src.alignment_runners import RUNNERS
from src.metrics import compute_all_metrics

sequences = list_sequences("h3h4")
print(f"Loaded {len(sequences)} sequences\n")

for method_name, runner in RUNNERS.items():
    print(f"--- Running {method_name} ---")
    try:
        alignment = runner(sequences)
        metrics = compute_all_metrics(alignment)
        for key, value in metrics.items():
            print(f"{key}: {value}")
        print()
    except RuntimeError as e:
        print(f"ERROR: {e}\n")