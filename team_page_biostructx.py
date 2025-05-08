import streamlit as st
from PIL import Image

# --- Main Heading ---
st.markdown("""
    <h1 style='text-align: center; color: #154360;'>👥 Meet the BioStructX Team</h1>
    <p style='text-align: center; font-size: 18px; color: #566573;'>
        Passionate individuals driving AI-powered structural bioinformatics.
    </p>
    <hr>
""", unsafe_allow_html=True)

# --- Sidebar Image (Optional Local) ---
#try:
#    st.sidebar.image("C:/Users/hp/OneDrive/Desktop/BioStructX/your_photo.jpg", caption="Mahesh Tamhane", width=160)
#except:
#    st.sidebar.warning("Add your photo to sidebar by replacing the placeholder path.")

# --- Section 1: Creator Info ---
st.markdown("""
### 🧑‍🔬 Project Lead
""")

img = Image.open("images/mahesh_tamhane.jpg").convert("RGB")
st.image(img, width=200)

st.markdown("""
**Mahesh Tamhane**  
*M.Sc. Bioinformatics, DES Pune University*  
Email: [maheshtamhane1214@gmail.com](mailto:maheshtamhane1214@gmail.com)  
GitHub: [https://github.com/MahiGitDES](https://github.com/MahiGitDES)

Mahesh leads the development and architecture of BioStructX with a vision to combine AI, structural bioinformatics, and modular workflows into a unified research platform. He is deeply invested in drug discovery, protein modeling, and web tool engineering.
""")

# --- Section 2: Mentorship ---
st.markdown("""
### 🧑‍🏫 Mentorship & Acknowledgements

Special thanks to:
- **Dr. Kushagra Kashyap**, Assistant Professor, Department of Life Sciences, DES Pune University
- All faculty and peers who provided constructive feedback during development

Your encouragement and guidance were instrumental in refining BioStructX.
""")

# --- Section 3: Join Us ---
st.markdown("""
### 🤝 Collaborate With Us

We welcome researchers, coders, and domain experts to join the BioStructX journey.  
Let's build smarter, accessible, and impactful tools for structural biology.

💬 Contact via [LinkedIn](https://www.linkedin.com/in/mahesht120598).

---
<p style='text-align: center;'>
Built with ❤️ by the BioStructX Team.
</p>
""", unsafe_allow_html=True)