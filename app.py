import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils import list_proteins, list_sequences
from src.alignment_runners import RUNNERS
from src.metrics import compute_all_metrics

st.set_page_config(page_title="MSA Method Comparator", layout="wide")
st.title("🧬 Multiple Sequence Alignment Comparator")
st.caption("Compare MUSCLE, Clustal Omega, and MAFFT across proteins of varying conservation.")

with st.sidebar:
    st.header("Configuration")
    protein = st.selectbox("Select protein", list_proteins())
    available = list_sequences(protein)
    species_choices = st.multiselect(
        "Select species",
        options=list(available.keys()),
        default=list(available.keys()),
    )
    method = st.selectbox("Alignment method", list(RUNNERS.keys()))
    run_button = st.button("Run Alignment", type="primary")

if run_button:
    st.divider()
st.subheader("📊 Full Benchmark: All Proteins × All Methods")
st.caption("Run every method on every protein to compare conservation representation across the board.")

run_all_button = st.button("Run Full Benchmark", type="secondary")

if run_all_button:
    results = []
    progress = st.progress(0, text="Starting benchmark...")
    total_runs = len(list_proteins()) * len(RUNNERS)
    current_run = 0

    for protein_name in list_proteins():
        protein_seqs = list_sequences(protein_name)
        if len(protein_seqs) < 2:
            continue
        for method_name, runner in RUNNERS.items():
            current_run += 1
            progress.progress(current_run / total_runs, text=f"Running {method_name} on {protein_name}...")
            try:
                alignment = runner(protein_seqs)
                metrics = compute_all_metrics(alignment)
                results.append({
                    "Protein": protein_name,
                    "Method": method_name,
                    **metrics
                })
            except RuntimeError as e:
                results.append({
                    "Protein": protein_name,
                    "Method": method_name,
                    "Alignment Length": "ERROR",
                    "% Conserved Positions": "ERROR",
                    "% Gaps": "ERROR",
                    "Column Score": "ERROR"
                })

    progress.empty()
    results_df = pd.DataFrame(results)
    st.session_state["benchmark_results"] = results_df

if "benchmark_results" in st.session_state:
    st.dataframe(st.session_state["benchmark_results"], use_container_width=True)

    st.markdown("#### Column Score by Protein and Method")
    chart_data = st.session_state["benchmark_results"]
    fig = px.bar(
        chart_data,
        x="Protein",
        y="Column Score",
        color="Method",
        barmode="group",
        title="Column Score by Protein and Method",
        labels={"Column Score": "Column Score (0–100)", "Protein": "Protein"},
    )
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    if len(species_choices) < 2:
        st.warning("Select at least 2 sequences to align.")
        st.stop()

    selected_records = {name: available[name] for name in species_choices}

    with st.spinner(f"Running {method}..."):
        try:
            alignment = RUNNERS[method](selected_records)
            st.session_state["alignment"] = alignment
            st.session_state["method"] = method
            st.session_state["protein"] = protein
        except RuntimeError as e:
            st.error(str(e))
            st.stop()

if "alignment" in st.session_state:
    alignment = st.session_state["alignment"]

    tab1, tab2 = st.tabs(["Alignment View", "Quality Metrics"])

    with tab1:
        st.subheader(f"{st.session_state['method']} — {st.session_state['protein']}")
        aln_text = "\n".join(f">{rec.id}\n{rec.seq}" for rec in alignment)
        st.code(aln_text, language=None)

    with tab2:
        metrics = compute_all_metrics(alignment)
        st.subheader("Quality Metrics")
        cols = st.columns(len(metrics))
        for col, (name, value) in zip(cols, metrics.items()):
            col.metric(name, value)
else:
    st.info("Configure your comparison in the sidebar and click **Run Alignment**.")