# train_model.py

from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# ----------------------------
# Helper Functions
# ----------------------------
def extract_ligand_features(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return [
        Descriptors.MolWt(mol),
        Descriptors.MolLogP(mol),
        Descriptors.TPSA(mol),
        Descriptors.NumRotatableBonds(mol)
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
    ("CCO", "MKTIIALSYIFCLVFA"),  # Ethanol + small peptide
    ("CC(C)Cc1ccc(O)cc1", "GAVLIMFWY"),  # Tyrosine + hydrophobic protein
    ("C1=CC=CN=C1", "MVKVYAPASSANMSVGFDVLGAAVTPVDGALLGDVVTVEAAETFSLNNLGQK"),  # Pyridine + long seq
    ("CC(=O)OC1=CC=CC=C1C(=O)O", "MEEPQSDPSVEPPLSQETFSDLWKLL"),  # Aspirin + human p53 peptide
    ("CCN(CC)CCCC(C)NC1=C2C=CC(=CC2=NC=C1)Cl", "MSLLLLTLLVAAALAAPASSS")  # Fluoxetine + signal peptide
]

X, y = [], []

for i, (smiles, seq) in enumerate(sample_data):
    ligand_feats = extract_ligand_features(smiles)
    protein_feats = extract_protein_features(seq)

    if ligand_feats and protein_feats:
        X.append(ligand_feats + protein_feats)
        # Simulated binding affinity (just for training)
        y.append(-6 - i * 1.2)  # e.g., -6.0, -7.2, ..., -10.8

X = np.array(X)
y = np.array(y)

# ----------------------------
# Train & Save Model
# ----------------------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "ml_model_rf.pkl")
print("✅ Trained and saved as ml_model_rf.pkl")
