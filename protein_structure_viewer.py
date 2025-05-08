# src/protein_structure_viewer.py

import streamlit as st
import requests
import py3Dmol
import re
from Bio.PDB.DSSP import dssp_dict_from_pdb_file
import tempfile
import pandas as pd

def load_protein_structure_viewer():
    st.title("🧬 Protein Structure Viewer")

    st.markdown("""
    View 3D structures using **UniProt ID**, **FASTA sequence**, or **PDB ID**. Structures are fetched from AlphaFold, RCSB, or can be uploaded directly.
    Secondary structure and domain information are computed if available.
    """)

    input_type = st.radio("Choose Input Type:", ["UniProt ID", "PDB ID", "FASTA Sequence"])

    with st.expander("🗞️ View Example Inputs"):
        tab1, tab2, tab3 = st.tabs(["UniProt ID", "PDB ID", "FASTA Sequence"])
        with tab1:
            st.code("P00533")
        with tab2:
            st.code("6VXX")
        with tab3:
            st.code(">sp|P69905|HBA_HUMAN Hemoglobin\nVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFD")

    user_input = st.text_area("Enter Input:", height=150)
    uploaded_pdb = st.file_uploader("📂 Or upload your own PDB file", type=["pdb"])


    def fetch_structure_from_pdb(pdb_id):
        url = f"https://files.rcsb.org/view/{pdb_id.lower()}.pdb"
        r = requests.get(url)
        return r.text if r.status_code == 200 else None

    def fetch_structure_from_alphafold(uniprot_id):
        url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
        r = requests.get(url)
        return r.text if r.status_code == 200 else None

    def extract_uniprot_from_fasta(fasta_seq):
        match = re.match(r">.*\|(\w+)\|", fasta_seq)
        return match.group(1) if match else None

    def display_structure(pdb_text, label):
        st.success(f"✅ Structure loaded for: {label}")
        viewer = py3Dmol.view(width=800, height=500)
        viewer.addModel(pdb_text, "pdb")
        viewer.setStyle({"cartoon": {"color": "spectrum"}})
        viewer.zoomTo()
        st.components.v1.html(viewer._make_html(), height=500, scrolling=False)

    def analyze_secondary_structure(pdb_text):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as f:
            f.write(pdb_text.encode())
            f.flush()
            try:
                dssp_dict, _ = dssp_dict_from_pdb_file(f.name)
                ss_counts = {"H": 0, "E": 0, "C": 0}
                for _, (_, _, ss, _, _, _, _) in dssp_dict.items():
                    if ss == "H": ss_counts["H"] += 1
                    elif ss == "E": ss_counts["E"] += 1
                    else: ss_counts["C"] += 1
                total = sum(ss_counts.values())
                for k in ss_counts:
                    ss_counts[k] = round((ss_counts[k] / total) * 100, 2)
                return ss_counts
            except Exception:
                return None

    def simulate_domain_annotation(pdb_text):
        domains = []
        if "DOMAIN" in pdb_text.upper() or "REGION" in pdb_text.upper():
            for line in pdb_text.splitlines():
                if any(tag in line for tag in ["DOMAIN", "REGION"]):
                    domains.append(line.strip())
        return domains if domains else None

    if st.button("🔍 View Structure"):
        if not user_input.strip() and not uploaded_pdb:
            st.warning("⚠️ Please provide a valid input or upload a structure file.")
        else:
            pdb_text = None
            label = ""

            if uploaded_pdb:
                pdb_text = uploaded_pdb.read().decode("utf-8")
                label = uploaded_pdb.name
            elif input_type == "PDB ID":
                pdb_text = fetch_structure_from_pdb(user_input.strip())
                label = user_input.strip().upper()
            elif input_type == "UniProt ID":
                pdb_text = fetch_structure_from_alphafold(user_input.strip())
                label = user_input.strip().upper()
            elif input_type == "FASTA Sequence":
                fasta_id = extract_uniprot_from_fasta(user_input.strip())
                if fasta_id:
                    pdb_text = fetch_structure_from_alphafold(fasta_id)
                    label = fasta_id
                else:
                    st.warning("🧬 FASTA input does not contain a UniProt ID header. Please upload a PDB model.")

            if pdb_text:
                display_structure(pdb_text, label)

                st.markdown("### 🎉 Secondary Structure Composition")
                ss_result = analyze_secondary_structure(pdb_text)
                if ss_result:
                    df = pd.DataFrame.from_dict(ss_result, orient='index', columns=["Percentage (%)"])
                    st.dataframe(df)
                else:
                    st.info("Secondary structure parsing not available for this file.")

                st.markdown("### 🌐 Domain Annotations (Simulated)")
                domains = simulate_domain_annotation(pdb_text)
                if domains:
                    for d in domains:
                        st.code(d)
                else:
                    st.info("No domain annotation tags found in the structure.")
            else:
                st.error("❌ Could not retrieve or interpret structure for the given input.")
                
    st.markdown("""
        <div class='nav-buttons'>
              <a href="/" target="_self">
              <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
              </a>
       </div>
    """, unsafe_allow_html=True)

