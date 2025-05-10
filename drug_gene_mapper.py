# src/drug_gene_mapper.py

import streamlit as st
from typing import Optional
import requests
import pandas as pd
from urllib.parse import quote

def load_drug_gene_mapper():
    st.title("🧠 Drug–Gene Mapper (BioStructX Module)")

    st.markdown("""
    This interactive module helps you explore **connections between drugs and genes**, visualize molecular structures,
    and uncover related **GO terms**, **disease links**, and **similar compounds**, all from trusted biomedical databases.
    """)

    user_input = st.text_input("🔍 Enter a Drug or Gene Name:")

    st.markdown("""
        <div class='nav-buttons'>
              <a href="/" target="_self">
              <button style="padding: 10px 20px; border-radius: 8px; background-color: #2980B9; color: white; border: none;">🔙 Back to Home</button>
              </a>
           </div>
        """, unsafe_allow_html=True)

    def get_pubchem_properties(name):
        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            res = requests.get(url)
            return res.json()['PropertyTable']['Properties'][0]
        except Exception as e:
            print(f"[PubChem Properties Error] {e}")
            return None

    def get_pubchem_similars(smiles, threshold=70):
        try:
            if not smiles or len(smiles) < 5:
                return []
            encoded_smiles = quote(smiles)
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/similarity/smiles/{encoded_smiles}/JSON?Threshold={threshold}&MaxRecords=5"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                return data.get('IdentifierList', {}).get('CID', [])
            return []
        except Exception as e:
            print(f"[Similarity Search Error] {e}")
            return []

    def get_pubchem_title(cid):
        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
            res = requests.get(url).json()
            return res['InformationList']['Information'][0]['Title']
        except:
            return "N/A"

    def get_pubchem_image(cid):
        return f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"

    def get_uniprot_entry(gene):
        try:
            url = f"https://rest.uniprot.org/uniprotkb/search?query={gene}&format=json&size=1"
            res = requests.get(url).json()
            return res['results'][0]
        except:
            return None

    def get_diseases(uniprot_id):
        try:
            url_primary = f"https://rest.uniprot.org/uniprotkb/search?query=accession:{uniprot_id}&format=tsv&fields=comment(DISEASE)"
            res = requests.get(url_primary)
            if res.status_code == 200 and "Comment (DISEASE)" in res.text:
                return pd.read_csv(pd.compat.StringIO(res.text), sep="\t")
            url_json = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
            res_json = requests.get(url_json)
            if res_json.status_code == 200:
                diseases = []
                data = res_json.json()
                for ref in data.get("comments", []):
                    if ref.get("commentType") == "DISEASE":
                        entry = ref.get("disease", {}).get("description", "")
                        if entry:
                            diseases.append({"Disease": entry})
                return pd.DataFrame(diseases)
            return None
        except:
            return None

    def get_go_term_name(go_id):
        try:
            url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_id}"
            headers = {"Accept": "application/json"}
            res = requests.get(url, headers=headers).json()
            return res["results"][0].get("name", "N/A")
        except:
            return "N/A"

    def get_go_terms(uniprot_id):
        try:
            url = f"https://www.ebi.ac.uk/QuickGO/services/annotation/search?geneProductId=UniProtKB:{uniprot_id}&limit=5"
            headers = {"Accept": "application/json"}
            res = requests.get(url, headers=headers).json()
            terms = []
            for g in res.get("results", []):
                go_id = g.get("goId", "")
                aspect = g.get("goAspect", "")
                name = g.get("goName") or get_go_term_name(go_id)
                terms.append({"GO ID": go_id, "Aspect": aspect, "Term": name})
            return pd.DataFrame(terms)
        except:
            return None

    if user_input:
        st.subheader(f"Results for: `{user_input}`")

        st.markdown("### 💊 Drug Information (PubChem)")
        props = get_pubchem_properties(user_input)
        smiles = None
        if props:
            smiles = props['CanonicalSMILES']
            st.write(props)
            image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{user_input}/PNG"
            st.image(image_url, caption="Structure from PubChem", width=250)
            st.markdown(f"[🔗 View on PubChem](https://pubchem.ncbi.nlm.nih.gov/#query={user_input})")
        else:
            st.warning("❌ No drug found on PubChem. Trying input as SMILES...")
            smiles = user_input

        st.markdown("### 🧬 Top 5 Similar Compounds")
        similar_cids = get_pubchem_similars(smiles)
        if similar_cids:
            data = [(cid, get_pubchem_title(cid), get_pubchem_image(cid)) for cid in similar_cids]
            df_sim = pd.DataFrame(data, columns=["CID", "Title", "Image URL"])
            for _, row in df_sim.iterrows():
                st.image(row["Image URL"], width=150)
                st.write(f"🔹 **CID:** {row['CID']}, **Title:** {row['Title']}")
                st.markdown(f"[View on PubChem](https://pubchem.ncbi.nlm.nih.gov/compound/{row['CID']})")
        else:
            st.warning("⚠️ No similar compounds found. Try another drug name or a valid canonical SMILES.")

        st.markdown("### 🧬 Gene / Protein Information (UniProt)")
        gene_data = get_uniprot_entry(user_input)
        if gene_data:
            uniprot_id = gene_data['primaryAccession']
            gene_name = gene_data.get('genes', [{'geneName': {'value': 'N/A'}}])[0]['geneName']['value']
            protein_name = gene_data['proteinDescription']['recommendedName']['fullName']['value']
            organism = gene_data['organism']['scientificName']

            st.write(f"**UniProt ID:** {uniprot_id}")
            st.write(f"**Gene Name:** {gene_name}")
            st.write(f"**Protein Name:** {protein_name}")
            st.write(f"**Organism:** {organism}")
            st.markdown(f"[View on UniProt](https://www.uniprot.org/uniprotkb/{uniprot_id})")

            st.markdown("### 🧠 GO Functional Annotations (QuickGO)")
            go_df = get_go_terms(uniprot_id)
            if go_df is not None and not go_df.empty:
                st.dataframe(go_df)
            else:
                st.info("No GO terms found for this protein.")

            st.markdown("### 🧩 Disease Associations (UniProt)")
            disease_df = get_diseases(uniprot_id)
            if disease_df is not None and not disease_df.empty:
                st.dataframe(disease_df)
            else:
                st.info("No disease data found for this protein. Try a reviewed UniProt ID like P00533.")
        else:
            st.warning("❌ Gene/Protein not found in UniProt.")


# --- Entry point for standalone run ---
if __name__ == "__main__":
    load_drug_gene_mapper()
