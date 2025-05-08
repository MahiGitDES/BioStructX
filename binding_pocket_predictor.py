import streamlit as st
import os
import numpy as np
from Bio.PDB import PDBParser, DSSP
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import py3Dmol
import tempfile
import streamlit.components.v1 as components

def load_binding_pocket_predictor():
    st.title("🤖 AI-Based Binding Pocket Predictor")
    st.markdown("""
    Upload a **protein structure (PDB)** and optionally a **ligand (SDF or MOL2)** file to:
    - Predict potential **binding pocket residues** using an AI model.
    - Visualize predicted residues and ligand in 3D with `py3Dmol`.
    """)

    # Upload protein
    pdb_file = st.file_uploader("📁 Upload a Protein Structure (.pdb)", type=["pdb"])
    ligand_file = st.file_uploader("💊 Optional: Upload Ligand File (.mol2 or .sdf)", type=["mol2", "sdf"])

    if pdb_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as temp_pdb:
            temp_pdb.write(pdb_file.read())
            temp_pdb_path = temp_pdb.name

        if ligand_file:
            ligand_ext = ligand_file.name.split('.')[-1]
            ligand_path = os.path.join(tempfile.gettempdir(), f"ligand.{ligand_ext}")
            with open(ligand_path, "wb") as f:
                f.write(ligand_file.read())
        else:
            ligand_path = None

        # Extract features
        def extract_residue_features(pdb_path):
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure("prot", pdb_path)
            model = structure[0]

            try:
                dssp = DSSP(model, pdb_path)
            except Exception as e:
                st.error(f"❌ DSSP failed. Ensure DSSP is installed: {e}")
                return None, None, None

            features = []
            res_ids = []
            atom_coords = []
            for key in dssp.keys():
                res = dssp[key]
                chain = key[0]
                resnum = key[1]
                aa = res[1]
                asa = res[3]
                phi = res[4]
                psi = res[5]
                hydrophobic = 1 if aa in "AVILMFYW" else 0
                features.append([asa, phi, psi, hydrophobic])
                res_ids.append((chain, resnum, aa))
                try:
                    atom = model[chain][resnum]['CA']
                    atom_coords.append(atom.coord)
                except:
                    atom_coords.append(None)
            return np.array(features), res_ids, atom_coords

        # Simulated RF model
        def simulate_model():
            X_dummy = np.random.rand(100, 4)
            y_dummy = np.random.randint(0, 2, 100)
            model = RandomForestClassifier().fit(X_dummy, y_dummy)
            scaler = StandardScaler().fit(X_dummy)
            return model, scaler

        # Predict and visualize
        features, res_ids, coords = extract_residue_features(temp_pdb_path)
        if features is not None:
            model, scaler = simulate_model()
            predictions = model.predict(scaler.transform(features))

            # Get predicted pocket residues and their coordinates
            pocket_residues = [res_ids[i] for i, pred in enumerate(predictions) if pred == 1]
            pocket_coords = [coords[i] for i, pred in enumerate(predictions) if pred == 1 and coords[i] is not None]

            st.success(f"✅ Found {len(pocket_residues)} predicted pocket residues.")
            if pocket_residues:
                st.markdown("### 🧬 Predicted Pocket Residues")
                st.code(", ".join([f"{c}:{r}{aa}" for c, r, aa in pocket_residues]))

            st.markdown("### 🔬 3D Visualization with py3Dmol")
            view = py3Dmol.view(width=700, height=500)
            view.addModel(open(temp_pdb_path).read(), 'pdb')
            view.setStyle({'cartoon': {'color': 'spectrum'}})

            # Highlight predicted residues
            for coord in pocket_coords:
                view.addSphere({
                    "center": {"x": float(coord[0]), "y": float(coord[1]), "z": float(coord[2])},
                    "radius": 1.5,
                    "color": "red",
                    "opacity": 0.85
                })

            # Add ligand if uploaded
            if ligand_path and os.path.exists(ligand_path):
                with open(ligand_path, "r") as f:
                    ligand_data = f.read()
                view.addModel(ligand_data, ligand_ext.lower())
                view.setStyle({'model': -1}, {'stick': {}})

            view.zoomTo()
            components.html(view._make_html(), height=520, scrolling=False)

    else:
        st.info("📌 Upload a `.pdb` file to begin AI-based prediction.")

    st.markdown("""
    ---
    <div class='nav-buttons'>
        <a href="/" target="_self">
        <button style="padding: 10px 20px; border-radius: 8px; background-color: #2C3E50; color: white; border: none;">🔙 Back to Home</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

# Run directly
if __name__ == "__main__":
    load_binding_pocket_predictor()
