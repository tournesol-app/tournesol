import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Tournesol",
    page_icon="🌻",
    initial_sidebar_state="expanded",
)

st.title("Tournesol Data Visualization")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "This application allows to explore the public data of"
        " [tournesol.app](https://tournesol.app)."
    )
    st.markdown(
        "You can visualize the public dataset made of users' individual"
        " ratings and the collective scores computed by the Tournesol"
        " algorithms."
    )

with col2:
    image = Image.open("../frontend/public/logos/Tournesol_Logo.png")
    st.image(image, width=128)
