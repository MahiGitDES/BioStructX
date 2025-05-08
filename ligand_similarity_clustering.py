# src/ligand_similarity_clustering.py

import streamlit as st

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, Draw
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

def load_ligand_similarity_clustering():
    st.markdown("""
    Upload or input **multiple ligands** as SMILES or ChEMBL IDs.  
    We’ll compute their chemical fingerprints, apply **Hierarchical Clustering**, and display a 2D **PCA plot**.
    """)

    # --- Tabs ---
    tab1, tab2 = st.tabs(["🧪 Input Ligands", "📖 Example"])

    with tab2:
        st.markdown("### Example SMILES")
        st.code("""CCO
CCN
CCCC
CC(=O)O
C1=CC=CC=C1""", language="text")

        st.markdown("### Example ChEMBL IDs")
        st.code("""CHEMBL25
CHEMBL112
CHEMBL521
CHEMBL190
CHEMBL98""", language="text")

    # --- Helper Functions ---
    def smiles_to_fingerprint(smiles):
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
        arr = np.zeros((1,))
        DataStructs.ConvertToNumpyArray(fp, arr)
        return arr

    def get_smiles_from_chembl(chembl_id):
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return data.get("molecule_structures", {}).get("canonical_smiles")
        return None

    def mol_image(smiles):
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            img = Draw.MolToImage(mol, size=(150, 150))
            return img
        return None

    # --- Input Section ---
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
                    ligands = [get_smiles_from_chembl(i) for i in ids]

    # --- Clustering and Plot ---
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

            # --- Matplotlib Plot ---
            fig, ax = plt.subplots(figsize=(8, 6))
            scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="tab10", s=100, alpha=0.8)
            for i, smi in enumerate(valid_smiles):
                ax.annotate(f"{i+1}", (X_pca[i, 0], X_pca[i, 1]), fontsize=9)
            ax.set_title("Ligand Clustering (PCA + Hierarchical)", fontsize=14)
            ax.set_xlabel("PC1")
            ax.set_ylabel("PC2")
            st.pyplot(fig)

            # --- DataFrame ---
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

            # --- Images ---
            st.markdown("### 🖼️ Molecule Structures")
            for smi in df["SMILES"]:
                img = mol_image(smi)
                if img:
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.image(Image.open(buf), caption=smi, width=150)

            # --- Download CSV ---
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Results CSV", csv, "ligand_clusters.csv", "text/csv")

            # --- Result Notes ---
            st.markdown("### 📊 Result Analysis")
            st.info(f"""
- **{len(set(labels))} unique clusters** were identified from {len(valid_smiles)} ligands.
- Ligands in the **same cluster** are chemically similar based on their molecular fingerprints.
- The **PCA plot** shows ligands as points in 2D space:
  - **PC1 (Principal Component 1)** captures the largest variation in chemical structure.
  - **PC2 (Principal Component 2)** captures the second largest variation.
- Points close together on the plot are **structurally similar**, while distant points are **structurally different**.
""")

# --- Deployment Safe Entry Point ---
if __name__ == "__main__":
    st.set_page_config(page_title="🔗 Ligand Similarity Clustering & Visualization", layout="wide")
    load_ligand_similarity_clustering()
