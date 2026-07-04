import streamlit as st
import pandas as pd
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