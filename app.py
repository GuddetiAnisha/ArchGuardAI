from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from archguard.catalogue import load_catalogue
from archguard.evaluator import assess
from archguard.parser import normalize, parse_document

ROOT = Path(__file__).parent
CATALOGUE = ROOT / "requirements" / "synthetic_mars.yaml"
EXAMPLE = ROOT / "examples" / "sample_architecture.md"

st.set_page_config(page_title="ArchGuardAI", page_icon="🛡️", layout="wide")
st.title("ArchGuardAI")
st.caption("Traceable AI-assisted architecture verification — human review required")

with st.sidebar:
    st.header("Architecture input")
    mode = st.radio("Source", ["Example", "Paste text", "Upload document"])
    pasted = st.text_area("Architecture description", height=260, disabled=mode != "Paste text")
    upload = st.file_uploader("Markdown, text, JSON, or Mermaid", type=["md", "txt", "json", "mmd", "mermaid"],
                              disabled=mode != "Upload document")
    run = st.button("Run assessment", type="primary", use_container_width=True)
    st.divider()
    st.warning("The bundled requirements are synthetic examples. Do not upload confidential documents to an unapproved environment.")


def get_document() -> tuple[str, str] | None:
    if mode == "Example":
        return parse_document(EXAMPLE), EXAMPLE.name
    if mode == "Paste text":
        if not pasted.strip():
            st.error("Paste an architecture description first.")
            return None
        return normalize(pasted), "pasted-architecture"
    if not upload:
        st.error("Upload a document first.")
        return None
    path = Path(tempfile.gettempdir()) / Path(upload.name).name
    path.write_bytes(upload.getbuffer())
    return parse_document(path), upload.name


if run:
    item = get_document()
    if item:
        document, name = item
        metadata, requirements = load_catalogue(CATALOGUE)
        report = assess(document, requirements, metadata, name)
        rows = [{"Requirement": finding.requirement_id, "Title": finding.requirement_title,
                 "Category": finding.category, "Status": finding.status.value,
                 "Confidence": finding.confidence} for finding in report.findings]
        frame = pd.DataFrame(rows)
        a, b, c, d = st.columns(4)
        a.metric("Compliant", report.summary["COMPLIANT"])
        b.metric("Non-compliant", report.summary["NON_COMPLIANT"])
        c.metric("Not enough information", report.summary["NOT_ENOUGH_INFORMATION"])
        d.metric("Human review", len(report.findings))
        st.plotly_chart(px.bar(frame.groupby(["Status", "Category"]).size().reset_index(name="Count"),
                               x="Status", y="Count", color="Category", barmode="stack",
                               title="Findings by status and category"), use_container_width=True)
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.subheader("Traceable findings")
        for finding in report.findings:
            with st.expander(f"{finding.requirement_id} — {finding.requirement_title}: {finding.status.value}"):
                st.write(f"**Reasoning:** {finding.reasoning}")
                st.write(f"**Risk:** {finding.risk}")
                st.write(f"**Recommendation:** {finding.recommendation}")
                st.write(f"**Confidence:** {finding.confidence:.0%} · **Source:** {finding.source}")
                if finding.evidence:
                    st.write("**Evidence/context:**")
                    for evidence in finding.evidence:
                        st.code(evidence.excerpt)
                else:
                    st.info("No explicit evidence found.")
        payload = json.dumps(report.model_dump(mode="json"), indent=2)
        st.download_button("Download JSON report", payload, file_name="archguard-assessment.json",
                           mime="application/json")

st.info("A conclusive status is not an automatic approval. Qualified architects must validate scope, evidence, applicability, and implementation reality.")
