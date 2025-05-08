from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np
import requests
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# ----------------------------
# RDKit API Function
# ----------------------------
def get_rdkit_properties(smiles):
    url = "https://rdkit-api.onrender.com/compute"  # Replace with actual Render URL
    response = requests.post(url, json={"smiles": smiles})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed for SMILES: {smiles}")
        return None

# ----------------------------
# Feature Extraction
# ----------------------------
def extract_ligand_features(smiles):
    props = get_rdkit_properties(smiles)
    if props is None or "error" in props:
        return None
    return [
        props.get("MolWt"),
        props.get("LogP"),
        props.get("TPSA", 0),  # Optional fields can default to 0
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

# ----------------------------
# Sample Ligand–Protein Pairs (Simulated)
# ----------------------------
sample_data = [
    ("CCO", "MKTIIALSYIFCLVFA"),
    ("CC(C)Cc1ccc(O)cc1", "GAVLIMFWY"),
    ("C1=CC=CN=C1", "MVKVYAPASSANMSVGFDVLGAAVTPVDGALLGDVVTVEAAETFSLNNLGQK"),
    ("CC(=O)OC1=CC=CC=C1C(=O)O", "MEEPQSDPSVEPPLSQETFSDLWKLL"),
    ("CCN(CC)CCCC(C)NC1=C2C=CC(=CC2=NC=C1)Cl", "MSLLLLTLLVAAALAAPASSS")
]

X, y = [], []

for i, (smiles, seq) in enumerate(sample_data):
    ligand_feats = extract_ligand_features(smiles)
    protein_feats = extract_protein_features(seq)

    if ligand_feats and protein_feats:
        X.append(ligand_feats + protein_feats)
        y.append(-6 - i * 1.2)

X = np.array(X)
y = np.array(y)

# ----------------------------
# Train & Save Model
# ----------------------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "ml_model_rf.pkl")
print("✅ Trained and saved as ml_model_rf.pkl")
