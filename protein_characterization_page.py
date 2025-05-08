# src/protein_characterization_page.py

import streamlit as st
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import matplotlib.pyplot as plt
import requests

def load_protein_characterization():
    # --- Header ---
    st.title("🧪 Protein Characterization")
    st.markdown("Upload or paste a protein sequence to compute physicochemical properties and GO-based functional prediction.")

    # --- Sequence Input ---
    seq_input = st.text_area("🔤 Enter Protein Sequence or FASTA:", height=200)

    def extract_sequence(text):
        lines = text.strip().splitlines()
        if lines and lines[0].startswith(">"):
            return "".join(lines[1:])  # Remove FASTA header
        return text.strip()

    def characterize_protein(seq):
        try:
            protein = ProteinAnalysis(seq)
            aa_percent = protein.get_amino_acids_percent()
            return {
                "Length": len(seq),
                "Molecular Weight": round(protein.molecular_weight(), 2),
                "Aromaticity": round(protein.aromaticity(), 3),
                "Instability Index": round(protein.instability_index(), 2),
                "Isoelectric Point (pI)": round(protein.isoelectric_point(), 2),
                "GRAVY": round(protein.gravy(), 3),
                "Extinction Coefficient": protein.molar_extinction_coefficient(),
                "Amino Acid Percent": aa_percent
            }
        except Exception as e:
            st.error(f"⚠️ Error analyzing protein: {e}")
            return None

    if seq_input:
        seq = extract_sequence(seq_input)
        if not seq.isalpha():
            st.warning("Sequence must contain only alphabetic characters (amino acids).")
        else:
            results = characterize_protein(seq)
            if results:
                st.subheader("🧬 Protein Properties")

                col1, col2, col3 = st.columns(3)
                col1.metric("Length", results["Length"])
                col1.metric("Mol. Weight", f"{results['Molecular Weight']} Da")

                col2.metric("Isoelectric Point", results["Isoelectric Point (pI)"])
                col2.metric("Instability Index", results["Instability Index"])

                col3.metric("Aromaticity", results["Aromaticity"])
                col3.metric("GRAVY", results["GRAVY"])

                st.markdown("### 🔦 Extinction Coefficient")
                st.code(f"{results['Extinction Coefficient']} (M⁻¹ cm⁻¹) → Absorbance at 280nm due to Tyr, Trp, and Cys.")

                st.markdown("### 🧪 Amino Acid Composition")
                aa_percent = results["Amino Acid Percent"]
                fig, ax = plt.subplots(figsize=(6, 6))
                top10 = dict(sorted(aa_percent.items(), key=lambda x: x[1], reverse=True)[:10])
                ax.pie(top10.values(), labels=top10.keys(), autopct="%1.1f%%", startangle=140)
                ax.set_title("Top 10 Amino Acids by Percentage")
                st.pyplot(fig)

    # --- GO Annotation ---
    st.markdown("---")
    st.markdown("### 🧠 Functional Prediction via UniProt & GO")

    uniprot_id = st.text_input("🔍 Enter UniProt ID to fetch GO terms (e.g., P69905):")

    def fetch_go_terms(uniprot_id):
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            go_terms = []
            for db_ref in data.get("uniProtKBCrossReferences", []):
                if db_ref["database"] == "GO":
                    go_terms.append(db_ref["id"])
            return list(set(go_terms))
        except:
            return []

    def get_go_term_name(go_id):
        url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_id}"
        try:
            r = requests.get(url, headers={"Accept": "application/json"})
            if r.status_code == 200:
                return r.json()["results"][0]["name"]
        except:
            return None

    if uniprot_id:
        go_ids = fetch_go_terms(uniprot_id)
        if go_ids:
            st.success(f"✅ Found {len(go_ids)} GO terms.")
            with st.spinner("Fetching GO term descriptions..."):
                go_data = [(go, get_go_term_name(go)) for go in go_ids[:15]]
            st.markdown("### 📖 Gene Ontology Terms")
            st.caption("Biological processes, molecular functions, and cellular components:")
            for go_id, term in go_data:
                if term:
                    st.markdown(f"- **{go_id}** → _{term}_")
                else:
                    st.markdown(f"- **{go_id}** → *(Name unavailable)*")
        else:
            st.warning("⚠️ No GO terms found for this UniProt ID.")

# Optional: Allow standalone execution
if __name__ == "__main__":
    #st.set_page_config(page_title="Protein Characterization", layout="wide")
    load_protein_characterization()
