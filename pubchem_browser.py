# src/pubchem_browser.py

import streamlit as st
import requests

# --- Deploy-Compatible Entry Point ---
def load_pubchem_browser():
    st.title("🧪 PubChem Compound Browser")

    cid = st.text_input("Enter PubChem Compound CID (e.g., 2244):")

    if cid:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
        response = requests.get(url)

        if response.status_code == 200:
            props = response.json().get("PropertyTable", {}).get("Properties", [{}])[0]
            st.markdown(f"**IUPAC Name:** {props.get('IUPACName', 'N/A')}")
            st.markdown(f"**Molecular Formula:** {props.get('MolecularFormula', 'N/A')}")
            st.markdown(f"**Molecular Weight:** {props.get('MolecularWeight', 'N/A')}")
        else:
            st.error("❌ Compound not found. Please check the CID.")
    
    st.markdown("""
        <div class='nav-buttons'>
              <a href="/" target="_self">
              <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
              </a>
           </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="PubChem Browser", page_icon="🧪", layout="wide")
    load_pubchem_browser()
