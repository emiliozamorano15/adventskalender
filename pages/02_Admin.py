import streamlit as st
import json
import os
from dotenv import load_dotenv
from datetime import date, datetime

# Load configuration from .env file
load_dotenv()

# --- Configuration ---
DATA_FILE = "advent_messages.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
KID_1_NAME = os.getenv("KID_1_NAME", "Kid 1")
KID_2_NAME = os.getenv("KID_2_NAME", "Kid 2")
CALENDAR_YEAR = os.getenv("CALENDAR_YEAR", date.today().year)
CALENDAR_MONTH = os.getenv("CALENDAR_MONTH", 12)
# Added DEBUG_MODE for clarity, though it's primarily used in Door_Message.py
DEBUG_MODE = os.getenv("DEBUG_MODE", 'False').lower() in ('true', '1', 't')


# --- Data Handling Functions ---

def load_data():
    """Load messages from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # FIX: Defensive cleaning: Strip whitespace from Date field on load
                for d in data:
                    if 'Date' in d and isinstance(d['Date'], str):
                        d['Date'] = d['Date'].strip()
                return data
        except Exception as e:
            st.error(f"Error loading JSON data: {e}")
            return []
    st.warning("Advent messages JSON file not found. Starting with empty data.")
    return []

def validate_data(data):
    """Ensure all rows have a valid YYYY-MM-DD date."""
    for i, row in enumerate(data):
        date_str = row.get('Date')
        # The date string should already be stripped from load_data, but we re-check robustness
        if not date_str or not isinstance(date_str, str):
            st.error(f"Validation failed on row {i+1}: 'Date' field is empty or not a string.")
            return False
        try:
            # Check for correct date format
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            st.error(f"Validation failed on row {i+1}: 'Date' value '{date_str}' is not in YYYY-MM-DD format.")
            return False
    return True


def save_data(data):
    """Save the list of message dictionaries to the JSON file."""
    
    # 1. Validate data before saving
    if not validate_data(data):
        st.error("Data save canceled due to validation errors. Please check the 'Date' column.")
        return
        
    # 2. Proceed with saving if valid
    try:
        # Sort data by Date string for clean display
        data.sort(key=lambda x: x.get('Date', '0000-00-00'))
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            # Use indent for readability in the JSON file
            json.dump(data, f, ensure_ascii=False, indent=4)
        st.success("Message data saved successfully!")
    except Exception as e:
        st.error(f"Error saving JSON data: {e}")


# --- Authentication ---

def check_password():
    """Returns True if the user enters the correct password."""
    if not ADMIN_PASSWORD:
        st.error("ADMIN_PASSWORD not set in .env file.")
        st.stop()

    def password_entered():
        """Checks whether a password entered is correct."""
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Enter Admin Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password was incorrect, show input + error.
        st.text_input(
            "Enter Admin Password", type="password", on_change=password_entered, key="password"
        )
        st.error("Incorrect password 🚨")
        return False
    else:
        # Password is correct.
        return True


# --- Main Application ---

def admin_panel():
    """The main Streamlit admin page content."""
    st.set_page_config(page_title="🎄 Admin Panel", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background-color: #0d281a; color: #f7f3e8; }
        .stButton>button {
            background-color: #d11218; 
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            background-color: #8B0000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("🎄 Advent Calendar Admin Panel")
    st.subheader(f"Editing Messages for {CALENDAR_MONTH}/{CALENDAR_YEAR}")
    
    if DEBUG_MODE:
        st.warning("⚠️ DEBUG MODE IS ACTIVE: Time gating is disabled for users.")

    # Load data from JSON file
    initial_data = load_data()
    
    # Define column configurations for the editor
    column_config = {
        # Changed from "Day" NumberColumn to "Date" TextColumn
        "Date": st.column_config.TextColumn(
            "Door Date (YYYY-MM-DD)", help="Full date for the door (e.g., 2025-12-01)", required=True
        ),
        "Message_Kid1": st.column_config.TextColumn(
            f"{KID_1_NAME}'s Message", help="Message for Kid 1", width="large"
        ),
        "Message_Kid2": st.column_config.TextColumn(
            f"{KID_2_NAME}'s Message", help="Message for Kid 2", width="large"
        ),
        "Is_Active": st.column_config.CheckboxColumn(
            "Active", help="Is this door enabled?", default=True
        ),
    }

    st.markdown("### Message Data Editor")
    
    # Use st.data_editor to display and allow editing of the list of dictionaries
    # Set key to ensure data is updated correctly
    edited_data = st.data_editor(
        initial_data,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="message_editor"
    )

    if st.button("Save Changes to JSON File"):
        # The data editor returns a list of dictionaries (Python objects), which is what we need for JSON saving.
        save_data(edited_data)

    st.markdown("---")
    st.info("Remember to keep the 'Date' column unique and sequential (YYYY-MM-DD) for the Advent Calendar to work correctly.")


# --- Run App ---

if __name__ == "__main__":
    if check_password():
        admin_panel()
    else:
        st.info("Please enter the password to access the admin panel.")