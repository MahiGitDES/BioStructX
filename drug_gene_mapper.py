import streamlit as st
from typing import Optional
import requests
import pandas as pd
import re

def load_drug_gene_mapper():
    st.set_page_config(page_title="Drug–Gene Mapper", layout="wide")
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

    def is_smiles(string):
        return bool(re.match(r"^[A-Za-z0-9@+\-\[\]=#$().\\/]+$", string)) and "=" in string

    def get_pubchem_properties_by_name(name):
        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            res = requests.get(url)
            return res.json()['PropertyTable']['Properties'][0]
        except:
            return None

    def get_pubchem_properties_by_smiles(smiles):
        try:
            encoded = requests.utils.quote(smiles)
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/cids/JSON"
            cid_res = requests.get(cid_url)
            cids = cid_res.json().get("IdentifierList", {}).get("CID", [])
            if not cids:
                return None
            cid = cids[0]
            prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            prop_res = requests.get(prop_url)
            return prop_res.json()['PropertyTable']['Properties'][0]
        except:
            return None

    def get_pubchem_similars(smiles, threshold=70):
        try:
            encoded_smiles = requests.utils.quote(smiles)
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/similarity/smiles/{encoded_smiles}/cids/JSON?Threshold={threshold}&MaxRecords=5"
            res = requests.get(url)
            res.raise_for_status()
            cids = res.json().get('IdentifierList', {}).get('CID', [])
            similar_props = []
            for cid in cids:
                prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES,IUPACName/JSON"
                prop_res = requests.get(prop_url)
                prop_res.raise_for_status()
                props = prop_res.json()['PropertyTable']['Properties'][0]
                similar_props.append({
                    "CID": cid,
                    "Title": props.get("IUPACName", "N/A"),
                    "SMILES": props.get("CanonicalSMILES", "N/A"),
                    "ImageURL": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                })
            return similar_props
        except Exception as e:
            print(f"Error fetching similar compounds: {e}")
            return []

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

        props = get_pubchem_properties_by_smiles(user_input) if is_smiles(user_input) else get_pubchem_properties_by_name(user_input)

        if props:
            st.write(props)
            image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{props['IUPACName']}/PNG"
            st.image(image_url, caption="Structure from PubChem", width=250)
            st.markdown(f"[🔗 View on PubChem](https://pubchem.ncbi.nlm.nih.gov/#query={props['IUPACName']})")

            st.markdown("### 🧬 Top 5 Similar Compounds (SMILES)")
            similar_props = get_pubchem_similars(props['CanonicalSMILES'])
            if similar_props:
                for compound in similar_props:
                    st.image(compound['ImageURL'], width=150)
                    st.write(f"🔹 **CID:** {compound['CID']}")
                    st.write(f"🔹 **Title:** {compound['Title']}")
                    st.write(f"🔹 **SMILES:** `{compound['SMILES']}`")
                    st.markdown(f"[View on PubChem](https://pubchem.ncbi.nlm.nih.gov/compound/{compound['CID']})")
            else:
                st.warning("⚠️ No similar compounds found. Try another drug or use a canonical SMILES format.")
        else:
            st.warning("❌ No drug found on PubChem.")

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
