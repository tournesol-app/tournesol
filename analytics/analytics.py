import streamlit as st
from PIL import Image

from pages import page_public_dataset, page_tournesol_scores

st.session_state.data = None

PAGES = {
    "Comparisons Public Dataset": page_public_dataset,
    "Tournesol Scores": page_tournesol_scores,
}

# === Side bar ==================================

image = Image.open("../frontend/public/logos/Tournesol_Logo.png")
st.sidebar.image(image, width=256)

st.sidebar.title("Tournesol data visualization")

st.sidebar.markdown(
    "This application has been created to explore the public dataset"
    " of [tournesol.app](https://tournesol.app)"
)

# Page navigation
selection = st.sidebar.radio("Navigation", list(PAGES.keys()))
page = PAGES[selection]
page.app()
