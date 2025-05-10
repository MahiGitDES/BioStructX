import streamlit as st
import requests
import pandas as pd
import py3Dmol

# DSSP API endpoint
DSSP_API_URL = "https://biostructx-dssp.onrender.com/dssp"

def load_binding_pocket_predictor():
    

    st.title("🧬 Binding Pocket Predictor with DSSP")
    st.markdown("Upload a PDB file to analyze secondary structure and visualize the protein.")

    # File uploader
    uploaded_file = st.file_uploader("Upload your PDB file", type=["pdb"])

    # Visualize PDB file with py3Dmol
    def render_pdb(pdb_string):
        view = py3Dmol.view(width=700, height=500)
        view.addModel(pdb_string, "pdb")
        view.setStyle({'cartoon': {'color': 'spectrum'}})
        view.zoomTo()
        return view

    if uploaded_file:
        st.success("✅ File uploaded.")

        pdb_content = uploaded_file.getvalue().decode("utf-8")
        
        # Show 3D structure
        with st.expander("🔬 Protein 3D Structure Viewer", expanded=True):
            view = render_pdb(pdb_content)
            st.components.v1.html(view._make_html(), height=500, scrolling=False)


        # Run DSSP
        if st.button("Run DSSP Analysis"):
            with st.spinner("Processing..."):
                try:
                    response = requests.post(DSSP_API_URL, files={"pdb": uploaded_file})
                    response.raise_for_status()
                    data = response.json()

                    if isinstance(data, dict) and "error" in data:
                        st.error(f"API Error: {data['error']}")
                    else:
                        df = pd.DataFrame(data)
                        st.success("DSSP results obtained!")
                        st.dataframe(df)

                        with st.expander("📊 Secondary Structure Chart"):
                            st.bar_chart(df["secondary_structure"].value_counts())
                except Exception as e:
                    st.error(f"Failed to run DSSP: {e}")
                
if __name__ == "__main__":
    st.set_page_config(page_title="Binding Pocket Predictor with DSSP", page_icon="🧬", layout="wide")
    load_binding_pocket_predictor()