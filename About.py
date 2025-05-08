import streamlit as st
# --- Page Configuration ---
# --- Custom CSS Styling ---
st.markdown("""
<style>
   .bio-card {
   background-color: #F4F9FF;
   border: 1px solid #D6EAF8;
   border-radius: 12px;
   padding: 25px;
   margin-top: 20px;
   font-family: 'Segoe UI', sans-serif;
   }
   .section-title {
   color: #154360;
   font-size: 1.4em;
   margin-top: 1em;
   font-weight: bold;
   }
   .nav-buttons {
   display: flex;
   justify-content: space-between;
   margin-top: 30px;
   }
</style>
""", unsafe_allow_html=True)
# --- Title ---
st.title("📘 About BioStructX")
# --- About Content ---
st.markdown("""
<div class='bio-card'>
   <div class='section-title'>👤 Creator & Vision</div>
   <p>BioStructX is a solo-engineered platform created by a <strong>Master's student in Bioinformatics</strong>, driven by a deep passion for <strong>structural biology</strong>, <strong>AI in drug discovery</strong>, and <strong>modular web-based research tools</strong>.</p>
   <div class='section-title'>🎯 Core Objective</div>
   <p>To develop a robust, modular platform that seamlessly connects structural bioinformatics workflows with modern machine learning.</p>
   <div class='section-title'>🔍 Feature Highlights</div>
   <ul>
      <li>🧬 3D Structure Viewer with AlphaFold & RCSB support</li>
      <li>🔗 Protein–Drug Mapping from UniProt, ChEMBL, and PubChem</li>
      <li>📈 Binding Affinity Estimation using ML-based descriptors</li>
      <li>🧠 Ligand Clustering via RDKit + PCA</li>
      <li>🌐 Evolutionary Divergence via MSA + RMSD + Phylogeny</li>
      <li>💬 Chat Assistant for AI-powered protein guidance</li>
   </ul>
   <div class='section-title'>⚙️ Power Stack</div>
   <ul>
      <li>Streamlit, py3Dmol, Biopython, RDKit, scikit-learn</li>
      <li>APIs: UniProt, AlphaFold, PubChem, ChEMBL, RCSB</li>
   </ul>
   <div class='section-title'>🌟 Unique Advantages</div>
   <ul>
      <li>💡 Structure-first workflows</li>
      <li>🧬 AI-aware modules</li>
      <li>🖥️ Web-based and install-free</li>
      <li>🎯 Research-relevant and expandable</li>
   </ul>
   <div class='section-title'>🚀 Future Enhancements</div>
   <ul>
      <li>📂 Multi-protein workspaces & study folders</li>
      <li>💉 Visual ADMET & toxicity dashboards</li>
      <li>🧬 Protein family clustering and alignment</li>
      <li>🧱 Drag-and-drop workflow composition</li>
      <li>🧠 AI assistant for suggesting next tools</li>
   </ul>
   <div class='nav-buttons'>
      <a href="/" target="_self">
      <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
      </a>
      <a href="https://github.com/YourGitHubUsername" target="_blank">
      <button style="padding: 10px 20px; border-radius: 8px; background-color: #2C3E50; color: white; border: none;">🌐 Visit GitHub</button>
      </a>
   </div>
</div>
""", unsafe_allow_html=True)