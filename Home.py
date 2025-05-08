import streamlit as st
import random
import requests
from streamlit_lottie import st_lottie

# --- Page Configuration ---
st.set_page_config(page_title="BioStructX", page_icon="🧬", layout="wide")

# --- Funny Bioinformatics Quotes ---
funny_lines = [
    "Running GROMACS: because molecules won't shake themselves.",
    "You say debugging, I say 'experimental feature'.",
    "My protein folds better than my laundry.",
    "Yes, I'm in a relationship... with my FASTA file.",
    "If it compiles, it's biology. If it runs, it's bioinformatics.",
    "Don't blame me, blame the alignment algorithm.",
    "SNP happens.",
    "I speak fluent Python, but only in 3-letter codes.",
    "Bioinformatics: where your errors have 1000 base pairs.",
    "No bugs here — just undocumented features in your genome.",
    "PCR? Pretty Cool Research!"
]
st.markdown(f"<p style='text-align:center; font-size:0.95em; color:gray;'>🧬 {random.choice(funny_lines)}</p>", unsafe_allow_html=True)

# --- Load Animation ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# --- Session Defaults ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "selected_module" not in st.session_state:
    st.session_state.selected_module = "Home"

# --- Dark Mode Toggle ---
toggle_col = st.columns([10, 1])[1]
with toggle_col:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# --- Theming ---
dark = st.session_state.dark_mode
nav_color = "#1A5276" if not dark else "#0d1117"
link_color = "white" if not dark else "#c9d1d9"
hover_color = "#F1C40F" if not dark else "#58a6ff"
bg_gradient = "linear-gradient(135deg, #e0f7fa, #f9fbe7)"
text_color = "#1A5276" if not dark else "#c9d1d9"
card_bg = "#F2F7FA" if not dark else "#161b22"
border_color = "#2E86C1" if not dark else "#30363d"
card_text = "#4B4B4B" if not dark else "#d0d6db"
footer_color = "gray" if not dark else "#8b949e"

# --- Styling ---
st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            backdrop-filter: blur(4px);
        }}
        .nav-container {{
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: {nav_color};
            padding: 12px 30px;
            border-radius: 0 0 10px 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .nav-title {{ font-size: 1.5em; font-weight: bold; color: {link_color}; }}
        .nav-links a {{
            color: {link_color}; margin-left: 20px; font-size: 1.1em; text-decoration: none;
        }}
        .nav-links a:hover {{ color: {hover_color}; }}
        .center-title {{ font-size: 3em; color: {text_color}; text-align: center; margin-top: 20px; }}
        .subtitle {{ text-align: center; font-size: 1.3em; color: gray; margin-bottom: 30px; }}
        .module-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            color: {card_text};
            animation: fadeIn 0.6s ease;
        }}
        .footer {{ text-align: center; color: {footer_color}; padding: 40px 0 10px; }}
        @keyframes fadeIn {{
            from {{opacity: 0; transform: translateY(20px);}}
            to {{opacity: 1; transform: translateY(0);}}
        }}
        .floating-btn {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1abc9c;
            color: white;
            padding: 12px 20px;
            border-radius: 50px;
            font-weight: bold;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 999;
        }}
    </style>
    <div class="nav-container">
        <div class="nav-title">🧬 BioStructX</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="https://github.com/your-username/BioStructX" target="_blank">GitHub</a>
            <a href="mailto:support@biostructx.org">Help</a>
        </div>
    </div>
    <a class='floating-btn' href="mailto:support@biostructx.org'>💬 Need Help?</a>
""", unsafe_allow_html=True)

# --- Title & Subtitle ---
st.markdown("<div class='center-title'>🧬 BioStructX: Structural Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Explore AI-powered tools for protein structure analysis, drug discovery, and evolutionary studies — all in one place.</p>", unsafe_allow_html=True)

# --- Display Lottie Animation ---
col1, col2 = st.columns(2)

with col1:
    bioinfo_left = load_lottieurl("https://assets6.lottiefiles.com/private_files/lf30_m6j5igxb.json")  # 👈 replace with any preferred bioinfo animation
    if bioinfo_left:
        st_lottie(bioinfo_left, height=280, speed=1, key="bioinfo_left")

with col2:
    protein_animation = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_3vbOcw.json")
    if protein_animation:
        st_lottie(protein_animation, height=280, speed=1, key="protein_anim")

# --- External Module Mapping ---
from binding_affinity_predictor import load_binding_affinity_predictor
from binding_pocket_predictor import load_binding_pocket_predictor
from drug_gene_mapper import load_drug_gene_mapper
from evolutionary_divergence import load_evolutionary_module
from ligand_similarity_clustering import load_ligand_similarity_clustering
from protein_characterization_page import load_protein_characterization
from protein_chat_page import load_protein_chat_page
from protein_structure_viewer import load_protein_structure_viewer
from uniprot_browser import load_uniprot_browser
from pubchem_browser import load_pubchem_browser
from chembl_browser import load_chembl_browser

module_map = {
    "binding_affinity": load_binding_affinity_predictor,
    "binding_pocket": load_binding_pocket_predictor,
    "drug_gene": load_drug_gene_mapper,
    "evolution": load_evolutionary_module,
    "ligand_cluster": load_ligand_similarity_clustering,
    "protein_character": load_protein_characterization,
    "protein_chat": load_protein_chat_page,
    "protein_struct": load_protein_structure_viewer,
    "uniprot": load_uniprot_browser,
    "pubchem": load_pubchem_browser,
    "chembl": load_chembl_browser
}

if st.session_state.selected_module != "Home":
    module_fn = module_map.get(st.session_state.selected_module)
    if module_fn:
        module_fn()
    st.stop()

# --- Home Page Cards ---
about_tab, team_tab = st.columns(2)
with about_tab:
    if st.button("📘 About BioStructX"):
        st.switch_page("pages/about_page_biostructx.py")
with team_tab:
    if st.button("👥 Meet the Team"):
        st.switch_page("pages/team_page_biostructx.py")

modules = [
    {"name": "Binding Affinity Predictor", "desc": "Predict binding affinity using ML models.", "fn": "binding_affinity"},
    {"name": "Binding Pocket Predictor", "desc": "Detect and visualize binding pockets.", "fn": "binding_pocket"},
    {"name": "Drug–Gene Mapper", "desc": "Map drug-gene interactions from public data.", "fn": "drug_gene"},
    {"name": "Evolutionary Divergence Visualizer", "desc": "Analyze divergence & conservation.", "fn": "evolution"},
    {"name": "Ligand Similarity Clustering", "desc": "Cluster similar ligands with PCA.", "fn": "ligand_cluster"},
    {"name": "Protein Characterization", "desc": "Analyze properties & GO terms.", "fn": "protein_character"},
    {"name": "Protein Chat Assistant", "desc": "AI assistant for protein queries.", "fn": "protein_chat"},
    {"name": "Protein Structure Viewer", "desc": "Explore protein structures in 3D.", "fn": "protein_struct"},
    {"name": "UniProt Browser", "desc": "Search UniProt proteins and get metadata.", "fn": "uniprot"},
    {"name": "PubChem Browser", "desc": "Search small molecules by name or CID.", "fn": "pubchem"},
    {"name": "ChEMBL Browser", "desc": "Browse ChEMBL drugs and targets.", "fn": "chembl"}
]

cols = st.columns(2)
for i, mod in enumerate(modules):
    with cols[i % 2]:
        st.markdown(f"<div class='module-card'><h4>{mod['name']}</h4><p>{mod['desc']}</p></div>", unsafe_allow_html=True)
        if st.button(f"👉 Open {mod['name']}", key=f"btn_{mod['fn']}"):
            st.session_state.selected_module = mod["fn"]
            st.rerun()

# --- Footer ---
st.markdown(f"""
    <div class="footer">
        © 2025 BioStructX | Crafted with ❤️ by Mahesh Tamhane using Streamlit + Bioinformatics APIs
    </div>
""", unsafe_allow_html=True)
