# src/protein_chat_page.py

import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# --- Load Environment Variables ---
load_dotenv()
client = os.getenv("OPENAI_API_KEY")


def load_protein_chat_page():
    st.markdown("<h1 style='text-align: center; color: #2E86C1;'>💬 Protein Chat Assistant</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; color: gray;'>
        Ask questions about proteins, drug discovery, structural biology, or related research topics.
        </p>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Query Input ---
    query = st.text_area("🧬 Enter your protein/drug-related research question:", height=150)

    # --- Settings ---
    with st.expander("⚙️ Advanced Settings"):
        use_gpt4 = st.checkbox("Use GPT-4 model", value=False)
        temp = st.slider("🎛️ Temperature (creativity)", min_value=0.0, max_value=1.0, value=0.7)
        max_tokens = st.slider("📏 Max Tokens", min_value=100, max_value=2048, value=512)

    # --- Example Prompts ---
    with st.expander("💡 Example Prompts"):
        st.markdown("""
        - What are the key binding domains of EGFR protein?  
        - Suggest potential druggable pockets in SARS-CoV-2 Mpro.  
        - How can AlphaFold assist in novel drug design?  
        - Which UniProt tools help in protein function prediction?  
        """)

    # --- Run Query ---
    if st.button("💡 Ask AI") and query.strip():
        with st.spinner("Thinking..."):
            try:
                model_name = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specialized in protein bioinformatics and drug discovery."},
                        {"role": "user", "content": query.strip()}
                    ]
                )
                answer = response.choices[0].message.content
                st.markdown("### 🧠 AI Answer")
                st.success(answer)

            except Exception as e:
                st.error(f"❌ Error generating response: {e}")


# --- Entry Point for Standalone Use ---
if __name__ == "__main__":
    st.set_page_config(page_title="Protein Chat Assistant", page_icon="💬", layout="wide")
    load_protein_chat_page()
