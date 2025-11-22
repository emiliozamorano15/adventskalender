import streamlit as st
import pandas as pd
from datetime import date
import calendar # Import added for month name conversion
from dotenv import load_dotenv
import os

# Load configuration from .env file
load_dotenv()

# --- Configuration & Data Loading ---
# FIX: Convert env variables to integers, providing defaults if not set or invalid
try:
    CALENDAR_YEAR = int(os.getenv("CALENDAR_YEAR", date.today().year))
except (ValueError, TypeError):
    CALENDAR_YEAR = date.today().year
    
try:
    CALENDAR_MONTH = int(os.getenv("CALENDAR_MONTH", 12))
except (ValueError, TypeError):
    CALENDAR_MONTH = 12

try:
    MAX_DAY = int(os.getenv("MAX_DAY", 24))
except (ValueError, TypeError):
    MAX_DAY = 24
    
DATA_FILE = "advent_messages.csv"

# Kid names from .env
KID_1_NAME = os.getenv("KID_1_NAME", "Kid 1")
KID_2_NAME = os.getenv("KID_2_NAME", "Kid 2")


def load_messages():
    """Load messages from the CSV file."""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    st.error("Error: Advent messages data file not found!")
    return pd.DataFrame()


def check_access(requested_day):
    """Checks if the requested day is currently accessible based on the real-world date."""
    today = date.today()
    
    # Get the month name dynamically for use in denial messages
    configured_month_name = calendar.month_name[CALENDAR_MONTH]
    
    # 1. Check if it's currently the configured month and year
    if today.year != CALENDAR_YEAR or today.month != CALENDAR_MONTH:
        return False, f"The Advent Calendar is configured for month {configured_month_name} of {CALENDAR_YEAR} and is not currently active."

    # 2. Check the date gate
    if requested_day < 1 or requested_day > MAX_DAY:
        return False, f"Invalid door number. Must be between 1 and {MAX_DAY}."

    if today.day >= requested_day:
        return True, None
    else:
        # FIX: Use the configured month name instead of hardcoded 'December'
        return False, f"It's only {configured_month_name} {today.day}. This door ({requested_day}) is still sealed!"


def main():
    """Main Streamlit application function for the door message."""
    st.set_page_config(page_title="🎄 Daily Message", layout="wide")
    
    df = load_messages()
    if df.empty:
        st.stop()

    # --- 1. Get the requested day and kid ID from URL parameters ---
    query_params = st.query_params
    requested_day_str = query_params.get("day", [None])[0]
    requested_kid_str = query_params.get("kid", [None])[0]

    try:
        requested_day = int(requested_day_str)
        # The kid parameter MUST be 1 or 2 (integers)
        requested_kid = int(requested_kid_str) 
        
        if requested_kid not in [1, 2]:
            raise ValueError("Invalid Kid ID. Kid parameter must be '1' or '2'.")

        # Ensure the day exists in the data frame
        if requested_day not in df['Day'].values:
            st.error("Error: This door number does not exist in the calendar data.")
            return

    except (TypeError, ValueError):
        # This catches errors if 'day' or 'kid' are missing, or if 'kid' is not an integer.
        st.markdown("## 🚫 Access Denied")
        st.warning("Please scan a valid QR code from your calendar door to view the message, or ensure the URL parameters (`day` and `kid`=1 or `kid`=2) are correctly provided as integers.")
        return

    # --- 2. Apply Time-Gating Logic and Extract Message ---
    is_accessible, reason = check_access(requested_day)
    message_row = df[df['Day'] == requested_day].iloc[0]
    
    # Determine the correct message column based on the kid ID
    message_column = f'Message_Kid{requested_kid}'
    kid_name = KID_1_NAME if requested_kid == 1 else KID_2_NAME

    message = message_row[message_column]
    is_active = message_row['Is_Active']

    st.markdown(
        """
        <style>
        .stApp { background-color: #0d281a; color: #f7f3e8; }
        .header-title { font-size: 3em; color: #d11218; text-align: center; font-family: 'Arial Black', sans-serif; margin-bottom: 0.5em; }
        .message-box { background-color: #56793A; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5); margin-top: 20px; }
        .secret-message { font-size: 1.5em; line-height: 1.6; color: #f7f3e8; font-family: 'Georgia', serif; }
        .error-message { font-size: 1.8em; color: #d11218; text-align: center; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f'<p class="header-title">{kid_name}\'s Secret of Door {requested_day}</p>', unsafe_allow_html=True)

    if not is_active:
        st.markdown(
            f'<div class="message-box" style="background-color: #8B0000;">'
            f'<p class="error-message">❌ This Door is Temporarily Disabled! ❌</p>'
            f'<p class="secret-message" style="text-align: center;">Dad/Mom is fixing something. Try again later!</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    elif is_accessible:
        # --- 3. Display Secret Message ---
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.image(f"https://placehold.co/150x150/F5C913/000000?text={requested_day}", caption=f"Door {requested_day}", width=150)

        with col2:
            st.markdown('<div class="message-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="secret-message">{message}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- 4. Display Denial Message ---
        st.markdown(
            f'<div class="message-box" style="background-color: #d11218;">'
            f'<p class="error-message">🛑 Hold Your Horses! 🛑</p>'
            f'<p class="secret-message" style="text-align: center;">{reason}</p>'
            f'<p class="secret-message" style="text-align: center;">Come back on {configured_month_name} {requested_day}!</p>' # Corrected Month Display
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()