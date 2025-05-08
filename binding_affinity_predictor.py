# src/binding_affinity_predictor.py

import streamlit as st
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import numpy as np
import joblib
import requests
import os
import matplotlib.pyplot as plt

# -------------------------------
# Replace with your actual Render API URL
RDKit_API_URL = "https://rdkit-api.onrender.com/compute"
# -------------------------------

def get_rdkit_properties(smiles):
    try:
        response = requests.post(RDKit_API_URL, json={"smiles": smiles})
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def load_binding_affinity_predictor():
    st.title("📈 Binding Affinity Predictor")
    st.markdown("""
    This tool predicts the **binding affinity** between a **ligand (SMILES)** and a **protein (sequence)**  
    using a machine learning model trained on structural and physicochemical descriptors.
    """)

    model_path = os.path.join(os.path.dirname(__file__), "ml_model_rf.pkl")
    if not os.path.exists(model_path):
        st.error(f"❌ ML model not found at: `{model_path}`.")
        st.stop()

    rf_model = joblib.load(model_path)

    def extract_ligand_features(smiles):
        props = get_rdkit_properties(smiles)
        if props is None or "error" in props:
            return None
        return [
            props.get("MolWt", 0),
            props.get("LogP", 0),
            props.get("TPSA", 0),
            props.get("NumRotatableBonds", 0)
        ]

    def extract_protein_features(sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return [
                analysis.molecular_weight(),
                analysis.aromaticity(),
                analysis.instability_index(),
                analysis.isoelectric_point(),
                analysis.gravy()
            ]
        except:
            return None

    def clean_sequence(seq_text):
        lines = seq_text.strip().splitlines()
        if lines and lines[0].startswith(">"):
            return "".join(lines[1:])
        return seq_text.strip()

    def get_smiles_from_chembl(chembl_id):
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return data.get("molecule_structures", {}).get("canonical_smiles")
        return None

    def get_sequence_from_uniprot(uniprot_id):
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
        r = requests.get(url)
        if r.status_code == 200:
            return clean_sequence(r.text)
        return None

    def plot_binding_affinity(pred_energy):
        fig, ax = plt.subplots(figsize=(6, 1.5))
        ax.set_xlim(-15, 0)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel("Binding Affinity (kcal/mol)")
        ax.set_title("Binding Affinity Range", fontsize=10)
        ax.barh(0.5, 5, left=-15, height=0.5, color="#ff5733", edgecolor="black", label="🔥 Strong (< -10)")
        ax.barh(0.5, 2, left=-10, height=0.5, color="#33c4ff", edgecolor="black", label="✅ Good (-10 to -8)")
        ax.barh(0.5, 2, left=-8, height=0.5, color="#f4d03f", edgecolor="black", label="⚠️ Moderate (-8 to -6)")
        ax.barh(0.5, 6, left=-6, height=0.5, color="#e74c3c", edgecolor="black", label="❌ Weak (> -6)")
        ax.axvline(pred_energy, color="black", linestyle="--", linewidth=2)
        ax.text(pred_energy, 0.7, f"Pred: {pred_energy:.2f}", ha="center", fontsize=9)
        ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize="x-small")
        st.pyplot(fig, use_container_width=True)

    # --- Ligand Input ---
    st.subheader("🧪 Ligand Input")
    ligand_input = st.text_input("Enter Ligand (SMILES or ChEMBL ID):")

    with st.expander("🧾 View Ligand Input Examples"):
        tab1, tab2 = st.tabs(["SMILES Format", "ChEMBL ID Format"])
        with tab1:
            st.code("CC(=O)OC1=CC=CC=C1C(=O)O", language="text")
        with tab2:
            st.code("CHEMBL25", language="text")

    if ligand_input.upper().startswith("CHEMBL"):
        smiles = get_smiles_from_chembl(ligand_input.upper())
        if smiles:
            st.success(f"🔗 SMILES from ChEMBL: `{smiles}`")
        else:
            st.error("❌ Could not retrieve SMILES.")
    else:
        smiles = ligand_input.strip()

    # --- Protein Input ---
    st.subheader("🧬 Protein Input")
    protein_input = st.text_area("Enter Protein Sequence (raw, FASTA, or UniProt ID):", height=150)
    protein_file = st.file_uploader("Or upload protein file", type=["fasta", "txt"])

    with st.expander("🧾 View Protein Input Examples"):
        tab1, tab2, tab3 = st.tabs(["Raw Sequence", "FASTA", "UniProt ID"])
        with tab1:
            st.code("MKTIIALSYIFCLVFA")
        with tab2:
            st.code(">sp|P12345|...\nMKTIIALSYIFCLVFA")
        with tab3:
            st.code("P25089")

    seq = None
    if protein_file:
        try:
            seq = clean_sequence(protein_file.read().decode("utf-8"))
        except:
            st.error("❌ Failed to read protein file.")
    elif protein_input and len(protein_input.strip()) <= 10:
        seq = get_sequence_from_uniprot(protein_input.strip())
        if seq:
            st.success("🧬 Sequence fetched from UniProt.")
        else:
            st.error("❌ UniProt fetch failed.")
    else:
        seq = clean_sequence(protein_input)

    # --- Prediction ---
    if st.button("⚙️ Predict Binding Affinity (ML)"):
        ligand_features = extract_ligand_features(smiles)
        protein_features = extract_protein_features(seq)

        if ligand_features is None:
            st.error("❌ Invalid SMILES.")
        elif protein_features is None:
            st.error("❌ Invalid protein sequence.")
        else:
            combined = np.array(ligand_features + protein_features).reshape(1, -1)
            prediction = rf_model.predict(combined)[0]
            predicted_energy = -prediction

            comment = (
                "🔥 Strong binding" if predicted_energy <= -10 else
                "✅ Good binding" if predicted_energy <= -8 else
                "⚠️ Weak binding" if predicted_energy <= -6 else
                "❌ Poor binding"
            )

            col1, col2 = st.columns([2, 1])
            with col1:
                st.success(f"🧠 Predicted Affinity: `{predicted_energy:.2f}` kcal/mol")
                st.info(comment)
            with col2:
                plot_binding_affinity(predicted_energy)

            st.markdown("""---""")
            st.markdown("""
            ### 🔍 Features Used:
            **Ligand (via RDKit API):**  
            - MolWt, LogP, TPSA, Rotatable Bonds  

            **Protein (Biopython):**  
            - MolWt, Aromaticity, Instability Index, pI, GRAVY
            """)
    
    st.markdown("""
        <div class='nav-buttons'>
              <a href="/" target="_self">
              <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
              </a>
       </div>
    """, unsafe_allow_html=True)

# Run directly
if __name__ == "__main__":
    load_binding_affinity_predictor()
