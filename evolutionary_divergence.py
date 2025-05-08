# src/evolutionary_divergence.py

import streamlit as st
from Bio import Phylo, SeqIO, AlignIO
from Bio.PDB import PDBParser, Superimposer, PDBIO
from io import StringIO
import tempfile
import subprocess
import os
import requests
import py3Dmol
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- FASTA & Tree ---
def fetch_fasta_from_uniprot(uniprot_ids):
    sequences = []
    for uid in uniprot_ids:
        url = f"https://rest.uniprot.org/uniprotkb/{uid}.fasta"
        r = requests.get(url)
        if r.status_code == 200:
            seq_records = list(SeqIO.parse(StringIO(r.text), "fasta"))
            sequences.extend(seq_records)
    return sequences

def run_clustalo_direct(sequences):
    with tempfile.TemporaryDirectory() as tmpdir:
        fasta_path = os.path.join(tmpdir, "input.fasta")
        aln_path = os.path.join(tmpdir, "aligned.aln")
        tree_path = os.path.join(tmpdir, "tree.dnd")

        SeqIO.write(sequences, fasta_path, "fasta")
        subprocess.run(["clustalo", "-i", fasta_path, "-o", aln_path,
                        "--guidetree-out", tree_path, "--force", "--auto", "--full"], check=True)

        alignment = AlignIO.read(aln_path, "fasta")
        tree = None
        try:
            with open(tree_path) as f:
                tree = Phylo.read(f, "newick")
        except FileNotFoundError:
            pass
    return alignment, tree

def plot_phylo_tree(tree):
    fig = plt.figure(figsize=(8, 6))
    Phylo.draw(tree, do_show=False)
    return fig

def fetch_domain_annotations(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    r = requests.get(url)
    domains = []
    if r.status_code == 200:
        data = r.json()
        features = data.get("features", [])
        for feat in features:
            if feat.get("type") in ["Domain", "Region"]:
                loc = feat.get("location", {})
                domains.append({
                    "description": feat.get("description", "Unknown"),
                    "start": loc.get("start", {}).get("value", "-"),
                    "end": loc.get("end", {}).get("value", "-")
                })
    return domains

def fetch_pdb_structure(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    r = requests.get(url)
    return r.text if r.status_code == 200 else None

# --- 3D Alignment ---
def apply_superimposition_and_return_pdbs(pdb_dict):
    parser = PDBParser(QUIET=True)
    structures, aligned_pdbs = {}, {}
    for name, content in pdb_dict.items():
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".pdb") as tmp:
            tmp.write(content)
            tmp.flush()
            structures[name] = parser.get_structure(name, tmp.name)

    ref_name = list(structures.keys())[0]
    ref_atoms = [res["CA"] for res in structures[ref_name][0].get_residues() if "CA" in res]

    for name, structure in structures.items():
        if name == ref_name:
            aligned_pdbs[name] = pdb_dict[name]
            continue
        mobile_atoms = [res["CA"] for res in structure[0].get_residues() if "CA" in res]
        min_len = min(len(ref_atoms), len(mobile_atoms))
        si = Superimposer()
        si.set_atoms(ref_atoms[:min_len], mobile_atoms[:min_len])
        si.apply(structure.get_atoms())
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".pdb") as aligned_file:
            io = PDBIO()
            io.set_structure(structure)
            io.save(aligned_file.name)
            aligned_file.seek(0)
            aligned_pdbs[name] = aligned_file.read()
    return aligned_pdbs

def visualize_structures(pdb_dict):
    view = py3Dmol.view(width=700, height=500)
    for i, (name, pdb) in enumerate(pdb_dict.items()):
        view.addModel(pdb, "pdb")
        view.setStyle({'model': i}, {"cartoon": {"color": "spectrum"}})
    view.zoomTo()
    return view

def calculate_rmsd_from_pdbs(pdb_dict):
    parser = PDBParser(QUIET=True)
    structures = {}
    for name, content in pdb_dict.items():
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".pdb") as tmp:
            tmp.write(content)
            tmp.flush()
            structures[name] = parser.get_structure(name, tmp.name)

    names = list(structures)
    n = len(names)
    rmsd_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            fa = [res["CA"] for res in structures[names[i]][0].get_residues() if "CA" in res]
            ma = [res["CA"] for res in structures[names[j]][0].get_residues() if "CA" in res]
            min_len = min(len(fa), len(ma))
            si = Superimposer()
            si.set_atoms(fa[:min_len], ma[:min_len])
            rmsd = si.rms
            rmsd_matrix[i, j] = rmsd
            rmsd_matrix[j, i] = rmsd
    return names, rmsd_matrix

def load_evolutionary_module():
    input_type = st.radio("Choose input type:", ["UniProt IDs (for MSA + Tree + Domains)", "PDB IDs or Upload (for Structure + RMSD)"])

    user_input = st.text_area("🔬 Enter comma-separated UniProt or PDB IDs (e.g., P69905,P68871 or 1A3N):")
    fasta_text = st.text_area("📋 Paste FASTA sequences (optional)", height=160)
    fasta_file = st.file_uploader("📁 Upload FASTA file (optional)", type=["fasta", "fa", "txt"])
    uploaded_pdb_files = st.file_uploader("📁 Upload one or more PDB files", type="pdb", accept_multiple_files=True)

    custom_sequences = []

    if fasta_text.strip():
        try:
            custom_sequences += list(SeqIO.parse(StringIO(fasta_text), "fasta"))
            st.success(f"✅ {len(custom_sequences)} sequences from pasted FASTA.")
        except Exception as e:
            st.error(f"❌ Error in pasted FASTA: {e}")

    if fasta_file:
        try:
            uploaded_sequences = list(SeqIO.parse(fasta_file, "fasta"))
            custom_sequences += uploaded_sequences
            st.success(f"✅ {len(uploaded_sequences)} sequences from uploaded file.")
        except Exception as e:
            st.error(f"❌ Error in uploaded FASTA: {e}")

    if st.button("🔎 Analyze"):
        ids = [i.strip() for i in user_input.split(",") if i.strip()]

        if input_type.startswith("UniProt"):
            sequences = fetch_fasta_from_uniprot(ids) + custom_sequences
            if not sequences:
                st.error("❌ No sequences found.")
                return

            alignment, tree = run_clustalo_direct(sequences)

            st.subheader("🧬 Multiple Sequence Alignment:")
            st.code("\n".join(str(rec.seq) for rec in alignment), language='text')

            st.subheader("🧪 Conserved & Mutated Residues")
            alignment_strs = [str(record.seq) for record in alignment]
            seq_len = len(alignment[0])
            conservation_result = []

            for i in range(seq_len):
                column = [seq[i] for seq in alignment_strs]
                unique_res = set(column) - {"-", "X"}
                conservation_result.append("✔" if len(unique_res) == 1 else "✘")

            highlight = "".join(conservation_result)
            st.markdown(f"`{highlight}`")
            st.caption("✔ = conserved, ✘ = mutated (per position)")

            mut_report = "\n".join([f"Position {i+1}: {mark}" for i, mark in enumerate(conservation_result)])
            st.download_button("📥 Download Mutation Report", mut_report, file_name="mutation_summary.txt")

            if tree:
                st.subheader("🌳 Phylogenetic Tree")
                st.pyplot(plot_phylo_tree(tree))

            if ids:
                st.subheader("📌 Domain Annotations:")
                for uid in ids:
                    st.markdown(f"**{uid}**")
                    domains = fetch_domain_annotations(uid)
                    if domains:
                        st.dataframe(pd.DataFrame(domains))
                    else:
                        st.write("No domain info.")

        elif input_type.startswith("PDB"):
            pdb_dict = {}

            if uploaded_pdb_files:
                for file in uploaded_pdb_files:
                    pdb_dict[file.name] = file.read().decode("utf-8")

            for pid in ids:
                pdb_content = fetch_pdb_structure(pid)
                if pdb_content:
                    pdb_dict[pid] = pdb_content

            if not pdb_dict:
                st.error("❌ No valid PDB files or IDs.")
                return

            st.subheader("🧩 Superimposed 3D Structures:")
            aligned_pdbs = apply_superimposition_and_return_pdbs(pdb_dict)
            viewer = visualize_structures(aligned_pdbs)
            st.components.v1.html(viewer._make_html(), height=500)

            names, rmsd_matrix = calculate_rmsd_from_pdbs(aligned_pdbs)
            st.subheader("📐 RMSD Matrix (Å)")
            st.dataframe(pd.DataFrame(rmsd_matrix, index=names, columns=names).round(3))

            avg_rmsd = np.nanmean(rmsd_matrix[np.triu_indices_from(rmsd_matrix, k=1)])
            st.success(f"✅ Average RMSD across structures: **{avg_rmsd:.3f} Å**")


# Entry point
if __name__ == "__main__":
    st.set_page_config(page_title="Protein Evolutionary Divergence", page_icon="🌿", layout="wide")
    load_evolutionary_module()
