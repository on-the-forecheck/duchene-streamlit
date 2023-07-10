import streamlit as st
from PIL import Image

favicon = Image.open("./assets/otf_logo.png")

st.set_page_config(page_title="Facts about Matt Duchene", page_icon=favicon)

st.write(f"# Facts about Matt Duchene")

st.sidebar.success("Select an area for analysis above.")

st.markdown(
    """
    Matt Duchene got Predators fans in a tizzy last week with a few of his comments. But what's the real story?
    **👈 Select an area of analysis from the sidebar** to see for yourself!
    ## Data
    All data are from EvolvingHockey, analyzed by me, Chicken

"""
)
