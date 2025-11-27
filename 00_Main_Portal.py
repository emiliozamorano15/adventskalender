import streamlit as st
from dotenv import load_dotenv
import os

# Load configuration from .env file
load_dotenv()

st.set_page_config(page_title="🎄 Home", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d281a; /* Dark green background */
        color: #f7f3e8; /* Off-white text */
        text-align: center;
    }
    .main-title {
        font-size: 3.5em;
        color: #d11218; /* Festive red */
        font-family: 'Arial Black', sans-serif;
        margin-top: 1em;
    }
    .subtitle {
        font-size: 1.5em;
        color: #56793A;
        margin-bottom: 2em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="main-title">Calendario de Adviento 2025</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Escanea tu código QR para saber qué tienes de regalo!</p>', unsafe_allow_html=True)

st.image("assets/family-portrait.png", use_container_width=True)

st.sidebar.caption("Adventskalendar App")