# src/uniprot_browser.py

import streamlit as st
import requests

# --- Deploy-Compatible Entry Point ---
def load_uniprot_browser():
    st.title("🔬 UniProt Protein Browser")

    query = st.text_input("Enter UniProt ID (e.g., P00533):")

    if query:
        url = f"https://rest.uniprot.org/uniprotkb/{query}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            name = data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "No Name Found")
            organism = data.get("organism", {}).get("scientificName", "N/A")
            genes = ', '.join([g['geneName']['value'] for g in data.get('genes', [])])
            comments = data.get('comments', [])
            function = "No function annotation available."
            for comment in comments:
                if comment.get('commentType') == 'FUNCTION':
                    texts = comment.get('texts', [])
                    if texts:
                        function = texts[0].get('value', function)
                        break

            st.subheader(name)
            st.markdown(f"**Organism:** {organism}")
            st.markdown(f"**Gene Names:** {genes}")
            st.markdown(f"**Function:** {function}")
        else:
            st.error("❌ Protein not found. Please check the UniProt ID.")

if __name__ == "__main__":
    st.set_page_config(page_title="UniProt Browser", page_icon="🧬", layout="wide")
    load_uniprot_browser()
