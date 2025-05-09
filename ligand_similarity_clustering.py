# src/ligand_similarity_clustering.py

import streamlit as st
import numpy as np
import pandas as pd
import requests
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from io import StringIO

# RDKit API endpoint (replace if changed)
RDKit_API_URL = "https://rdkit-api.onrender.com/compute"

def load_ligand_similarity_clustering():
    st.title("🔗 Ligand Similarity Clustering & Visualization")

    st.markdown("""
    Upload or input **multiple ligands** as SMILES or ChEMBL IDs.  
    We’ll compute their chemical fingerprints via an RDKit API, apply **Hierarchical Clustering**, and display a 2D **PCA plot**.
    """)

    tab1, tab2 = st.tabs(["🧪 Input Ligands", "📖 Example"])

    with tab2:
        st.markdown("### Example SMILES")
        st.code("""CCO\nCCN\nCCCC\nCC(=O)O\nC1=CC=CC=C1""")
        st.markdown("### Example ChEMBL IDs")
        st.code("""CHEMBL25\nCHEMBL112\nCHEMBL521\nCHEMBL190\nCHEMBL98""")

    def smiles_to_fingerprint(smiles):
        try:
            response = requests.post(RDKit_API_URL, json={"smiles": smiles})
            if response.status_code == 200:
                data = response.json()
                return np.array(data.get("fingerprint"))
        except Exception as e:
            st.warning(f"❌ Error for {smiles}: {str(e)}")
        return None

    def get_smiles_from_chembl(chembl_id):
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return data.get("molecule_structures", {}).get("canonical_smiles")
        return None

    with tab1:
        st.subheader("📥 Input Ligands")
        input_method = st.radio("Choose input method:", ["SMILES List", "ChEMBL IDs"])
        ligands = []

        if input_method == "SMILES List":
            smiles_input = st.text_area("Paste SMILES strings (one per line):", height=200)
            if smiles_input:
                ligands = [s.strip() for s in smiles_input.splitlines() if s.strip()]

        elif input_method == "ChEMBL IDs":
            chembl_input = st.text_area("Paste ChEMBL IDs (one per line):", height=200)
            if chembl_input:
                ids = [i.strip().upper() for i in chembl_input.splitlines() if i.strip()]
                with st.spinner("Fetching SMILES from ChEMBL..."):
                    ligands = [get_smiles_from_chembl(i) for i in ids if get_smiles_from_chembl(i)]

    if ligands and st.button("🔍 Cluster & Visualize"):
        valid_smiles = []
        fps = []

        for smi in ligands:
            fp = smiles_to_fingerprint(smi)
            if fp is not None:
                valid_smiles.append(smi)
                fps.append(fp)

        if len(fps) < 2:
            st.warning("⚠️ Need at least 2 valid ligands for clustering.")
        else:
            X = np.array(fps)
            labels = AgglomerativeClustering(n_clusters=None, distance_threshold=5).fit_predict(X)
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)

            fig, ax = plt.subplots(figsize=(8, 6))
            scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="tab10", s=100, alpha=0.8)
            for i, smi in enumerate(valid_smiles):
                ax.annotate(f"{i+1}", (X_pca[i, 0], X_pca[i, 1]), fontsize=9)
            ax.set_title("Ligand Clustering (PCA + Hierarchical)", fontsize=14)
            ax.set_xlabel("PC1")
            ax.set_ylabel("PC2")
            st.pyplot(fig)

            df = pd.DataFrame({
                "Index": [i+1 for i in range(len(valid_smiles))],
                "SMILES": valid_smiles,
                "Cluster": labels
            })

            st.markdown("### 🧬 Clustered Ligands")
            cluster_filter = st.multiselect("Filter by cluster(s):", options=list(set(labels)))
            if cluster_filter:
                df = df[df["Cluster"].isin(cluster_filter)]
            st.dataframe(df)

            csv = df.to_csv(index=False)
            st.download_button("📥 Download Results CSV", csv, "ligand_clusters.csv", "text/csv")

            st.markdown("### 📊 Result Analysis")
            st.info(f"""
- **{len(set(labels))} clusters** identified from {len(valid_smiles)} ligands.
- Ligands in the **same cluster** share structural similarity.
- **PC1 & PC2** are principal components showing chemical variation.
""")

    st.markdown("""
        <div class='nav-buttons'>
              <a href="/" target="_self">
              <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
              </a>
       </div>
    """, unsafe_allow_html=True)

# Standalone run
if __name__ == "__main__":
    load_ligand_similarity_clustering()
