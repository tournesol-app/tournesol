import streamlit as st
from PIL import Image


st.title("Tournesol data visualization")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "This application has been created to explore the public dataset of"
        " [tournesol.app](https://tournesol.app). You can found information and visualization of"
        " the public dataset the aggregated results of the Tournesol algorithm."
    )

with col2:
    image = Image.open("../frontend/public/logos/Tournesol_Logo.png")
    st.image(image, width=128)
