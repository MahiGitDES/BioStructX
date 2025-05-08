# src/chembl_browser.py

import streamlit as st
import requests

# --- Deploy-Compatible Entry Point ---
def load_chembl_browser():
    st.title("💊 ChEMBL Drug/Target Browser")

    chembl_id = st.text_input("Enter ChEMBL ID (e.g., CHEMBL25):")

    if chembl_id:
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            st.markdown(f"**Pref Name:** {data.get('pref_name', 'N/A')}")
            st.markdown(f"**Molecule Type:** {data.get('molecule_type', 'N/A')}")
            st.markdown(f"**Max Phase:** {data.get('max_phase', 'N/A')} (Clinical Trials)")
            st.markdown(f"**ChEMBL URL:** [Open in ChEMBL](https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id})")
        else:
            st.error("❌ ChEMBL ID not found. Please check the ID.")

if __name__ == "__main__":
    st.set_page_config(page_title="ChEMBL Browser", page_icon="💊", layout="wide")
    load_chembl_browser()
