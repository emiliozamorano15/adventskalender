import streamlit as st
from dotenv import load_dotenv
import os

# Load configuration from .env file
load_dotenv()

st.set_page_config(page_title="🎄 Main Portal", layout="wide")

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

st.markdown('<h1 class="main-title">The Secret Advent Calendar Portal</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Scan your special QR Code to reveal the secret of your door!</p>', unsafe_allow_html=True)

# Image of a simple gift box, since this is the main landing page
# FIX: Replaced deprecated 'use_column_width=True' with 'use_container_width=True'
st.image("https://placehold.co/800x250/F5C913/0D281A?text=Scan+Your+Door+Code", use_container_width=True)

st.sidebar.caption("Advent Calendar App")