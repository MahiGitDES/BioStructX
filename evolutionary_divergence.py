# src/evolutionary_divergence.py

import streamlit as st
from Bio import Phylo, SeqIO, AlignIO
from Bio.PDB import PDBParser, Superimposer, PDBIO
from io import StringIO
import tempfile
import os
import requests
import py3Dmol
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

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

def run_clustalo_remote(sequences):
    fasta_str = ""
    for i, seq in enumerate(sequences):
        fasta_str += f">seq{i+1}\n{seq.seq}\n"

    submit_url = "https://www.ebi.ac.uk/Tools/services/rest/clustalo/run"
    params = {
        "sequence": fasta_str,
        "email": "maheshtamhane1214@gmail.com",
        "outfmt": "fa",
        "guidetreeout": "true",
        "dealign": "true"
    }

    response = requests.post(submit_url, data=params)
    if response.status_code != 200:
        st.error(f"❌ API error: {response.text}")
        raise Exception("❌ Clustal Omega submission failed.")

    job_id = response.text.strip()
    status_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/status/{job_id}"

    while True:
        status = requests.get(status_url).text
        if status == "FINISHED":
            break
        elif status == "ERROR":
            raise Exception("❌ Clustal Omega job failed.")
        time.sleep(3)

    aln_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/result/{job_id}/aln-fasta"
    tree_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/result/{job_id}/phylotree"

    aln_response = requests.get(aln_url)
    tree_response = requests.get(tree_url)

    tree_text = tree_response.text.strip()
    st.text(f"Returned Tree (Newick):\n{tree_text}")

    if not tree_text or tree_text in ["", "()"]:
        st.warning("⚠️ The returned phylogenetic tree is empty or invalid. Please try with more diverse or longer sequences.")
        return AlignIO.read(StringIO(aln_response.text), "fasta"), None

    alignment = AlignIO.read(StringIO(aln_response.text), "fasta")
    tree = Phylo.read(StringIO(tree_text), "newick")

    return alignment, tree

def plot_phylo_tree(tree):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, do_show=False, axes=ax)
    return fig

# The rest of the code remains unchanged...

# Entry point
if __name__ == "__main__":
    st.set_page_config(page_title="Protein Evolutionary Divergence", page_icon="🌿", layout="wide")
    load_evolutionary_module()
