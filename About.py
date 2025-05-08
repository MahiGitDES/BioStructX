import streamlit as st

st.set_page_config(page_title="About BioStructX", page_icon="📘", layout="wide")

st.markdown("""
    <style>
        .bio-card {
            background-color: #F4F9FF;
            border: 1px solid #D6EAF8;
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
        }
        .section-title {
            color: #154360;
            font-size: 1.6em;
            margin-top: 1em;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📘 About BioStructX")
st.markdown("""
<div class='bio-card'>
    <div class='section-title'>👤 Creator & Vision</div>
    BioStructX is a solo-engineered platform created by a **Master's student in Bioinformatics**, driven by a deep passion for **structural biology**, **AI in drug discovery**, and **modular web-based research tools**.

    <div class='section-title'>🎯 Core Objective</div>
    To develop a robust, modular platform that seamlessly connects structural bioinformatics workflows with modern machine learning.

    <div class='section-title'>🔍 Feature Highlights</div>
    - 🧬 3D Structure Viewer with AlphaFold & RCSB support  
    - 🔗 Protein–Drug Mapping from UniProt, ChEMBL, and PubChem  
    - 📈 Binding Affinity Estimation using ML-based descriptors  
    - 🧠 Ligand Clustering via RDKit + PCA  
    - 🌐 Evolutionary Divergence via MSA + RMSD + Phylogeny  
    - 💬 Chat Assistant for AI-powered protein guidance

    <div class='section-title'>⚙️ Power Stack</div>
    - Streamlit, py3Dmol, Biopython, RDKit, scikit-learn  
    - APIs: UniProt, AlphaFold, PubChem, ChEMBL, RCSB

    <div class='section-title'>🌟 Unique Advantages</div>
    - 💡 Structure-first workflows  
    - 🧬 AI-aware modules  
    - 🖥️ Web-based and install-free  
    - 🎯 Research-relevant and expandable

    <div class='section-title'>🚀 Future Enhancements</div>
    - 📂 Multi-protein workspaces & study folders  
    - 💉 Visual ADMET & toxicity dashboards  
    - 🧬 Protein family clustering and alignment  
    - 🧱 Drag-and-drop workflow composition  
    - 🧠 AI assistant for suggesting next tools
</div>
""", unsafe_allow_html=True)
