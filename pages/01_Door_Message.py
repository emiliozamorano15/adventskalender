import streamlit as st
import json
from datetime import date, datetime
import calendar
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
    
# Check for debugging mode
DEBUG_MODE = os.getenv("DEBUG_MODE", 'False').lower() in ('true', '1', 't')
    
# Change DATA_FILE to point to the new JSON file
DATA_FILE = "advent_messages.json"

# Kid names from .env
KID_1_NAME = os.getenv("KID_1_NAME", "Kid 1")
KID_2_NAME = os.getenv("KID_2_NAME", "Kid 2")


def load_data():
    """Load messages from the JSON file using standard library."""
    if os.path.exists(DATA_FILE):
        try:
            # Use 'utf-8' encoding explicitly for reliable loading of JSON/emojis
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # FIX: Defensive cleaning: Strip whitespace from Date field on load
                for d in data:
                    if 'Date' in d and isinstance(d['Date'], str):
                        d['Date'] = d['Date'].strip()
                return data
        except Exception as e:
            st.error(f"Error reading JSON data: {e}")
            return []
    st.error("Error: Advent messages JSON file not found!")
    return []


def check_access(requested_date_str):
    """Checks if the requested date is currently accessible based on the real-world date."""
    if DEBUG_MODE:
        return True, None # Bypasses all time-gating

    today = date.today()
    
    try:
        requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, f"Invalid date format in the URL or JSON data: {requested_date_str}. Must be YYYY-MM-DD."

    # 1. Check if it's currently the configured month and year
    configured_month_name = calendar.month_name[CALENDAR_MONTH]
    if today.year != CALENDAR_YEAR or today.month != CALENDAR_MONTH:
        return False, f"The Advent Calendar is configured for month {configured_month_name} of {CALENDAR_YEAR} and is not currently active."

    # 2. Check the date gate
    if today >= requested_date:
        return True, None
    else:
        # Use the configured month name instead of hardcoded 'December'
        return False, f"It's only {configured_month_name} {today.day}. This door ({requested_date_str}) is still sealed!"


def main():
    """Main Streamlit application function for the door message."""
    st.set_page_config(page_title="🎄 Daily Message", layout="wide")
    
    # Load data (list of dicts)
    data = load_data()
    if not data:
        st.stop()

    # --- 1. Get the requested date and kid ID from URL parameters ---
    query_params = st.query_params
    
    # Get the value for 'date'. It might be a string (observed bug) or a list (standard Streamlit).
    raw_date_value = query_params.get("date", [None])
    
    # Handle the two possible return types for a URL query parameter in Streamlit
    if isinstance(raw_date_value, list):
        # Standard Streamlit behavior: value is a list of strings
        requested_date_str_raw = raw_date_value[0] if raw_date_value and raw_date_value[0] else None
    elif isinstance(raw_date_value, str):
        # Non-standard behavior (observed in your debug): value is the string itself
        requested_date_str_raw = raw_date_value
    else:
        requested_date_str_raw = None
        
    requested_date_str = requested_date_str_raw # Initialize requested_date_str for the debugging block

    # --- DEBUGGING PRINTS (Before Strip) ---
    if DEBUG_MODE:
        st.subheader("⚠️ DEBUGGING: URL Query Parameters")
        st.code(f"Full st.query_params: {dict(query_params)}", language="python")
        st.code(f"Raw Date Value (from .get()): {raw_date_value} (Type: {type(raw_date_value)})", language="python")
        st.code(f"Raw Date String: '{requested_date_str_raw}' (Length: {len(requested_date_str_raw) if requested_date_str_raw else 0})", language="python")
    # --- END DEBUGGING PRINTS ---

    try:
        # Ensure the date string from the URL is also stripped for a clean comparison
        if not requested_date_str_raw:
             raise TypeError("Date parameter is missing.")
        
        # Use the raw string for the strip operation
        requested_date_str = requested_date_str_raw.strip() # Defensive strip for URL parameter
             
        # The kid parameter MUST be 1 or 2 (integers)
        requested_kid_str = query_params.get("kid", [None])[0]
        # We need to handle the kid parameter similar to the date if it's being returned as a bare string
        if isinstance(requested_kid_str, list):
             requested_kid_str = requested_kid_str[0]

        requested_kid = int(requested_kid_str) 
        
        if requested_kid not in [1, 2]:
            raise ValueError("Invalid Kid ID. Kid parameter must be '1' or '2'.")
        
        # --- DEBUGGING PRINTS (After Strip & JSON Load) ---
        if DEBUG_MODE:
            st.code(f"Stripped Date used for Lookup: '{requested_date_str}' (Length: {len(requested_date_str)})", language="python")
            
            # Show what dates are loaded from the JSON for comparison
            data_dates = [d['Date'] for d in data if 'Date' in d]
            st.code(f"Dates Loaded from JSON (First 5): {data_dates[:5]}... Total: {len(data_dates)}", language="python")
        # --- END DEBUGGING PRINTS ---


        # Check if the date exists in the data
        # The data in 'data' is already stripped thanks to load_data()
        if not any(d['Date'] == requested_date_str for d in data):
            # This is the error we are trying to debug
            st.error("Error: This door date does not exist in the calendar data.")
            return
        
        # Extract the day number for display purposes
        requested_day = int(requested_date_str.split('-')[2]) 

    except (TypeError, ValueError) as e:
        # This catches errors if 'date' or 'kid' are missing, or if 'kid' is not an integer.
        st.markdown("## 🚫 Access Denied")
        st.warning(f"Please scan a valid QR code or ensure the URL parameters (`date`=YYYY-MM-DD and `kid`=1 or `kid`=2) are correctly provided. Error: {e}")
        return

    # --- 2. Apply Time-Gating Logic and Extract Message ---
    # Passed the date string to check_access
    is_accessible, reason = check_access(requested_date_str)
    
    # Find the data dictionary for the requested date
    # Updated retrieval key from 'Day' to 'Date'
    message_row = next((d for d in data if d.get('Date') == requested_date_str), None)
    
    if message_row is None:
        # This should theoretically be unreachable if the check above passes, but kept as a safeguard.
        st.error(f"Data for Date {requested_date_str} not found in the data.")
        return
        
    # Determine the correct message key based on the kid ID
    message_column = f'Message_Kid{requested_kid}'
    kid_name = KID_1_NAME if requested_kid == 1 else KID_2_NAME

    message = message_row.get(message_column, "Message not available.")
    is_active = message_row.get('Is_Active', False)
    
    # Get the configured month name for display purposes
    configured_month_name = calendar.month_name[CALENDAR_MONTH]

    st.markdown(
        """
        <style>
        .stApp { background-color: #0d281a; color: #f7f3e8; }
        .header-title { font-size: 3em; color: #d11218; text-align: center; font-family: 'Arial Black', sans-serif; margin-bottom: 0.5em; }
        .message-box { background-color: #56793A; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5); margin-top: 20px; }
        .secret-message { font-size: 1.5em; line-height: 1.6; color: #f7f3e8; font-family: 'Georgia', serif; }
        .error-message { font-size: 1.8em; color: #d11218; text-align: center; }
        /* Style for the image container to ensure images look good on all devices */
        .stImage { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5); }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Use the extracted day number for display
    st.markdown(f'<p class="header-title">{kid_name}\'s Secret of Door {requested_day}</p>', unsafe_allow_html=True)
    
    if DEBUG_MODE and is_accessible:
        st.warning("⚠️ DEBUG MODE ACTIVE: Time validation bypassed.")


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
        # Changed columns from [1, 4] to [3, 7] for ~30%/70% split
        col1, col2 = st.columns([3, 7]) 
        
        with col1:
            # Replaced placeholder image with the requested local file path
            st.image("./assets/family-portrait.png", 
                     caption=f"December {requested_day}", 
                     use_container_width=True)

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
            f'<p class="secret-message" style="text-align: center;">Come back on {requested_date_str}!</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()