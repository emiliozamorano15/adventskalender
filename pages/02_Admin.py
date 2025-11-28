import streamlit as st
import json
import os
from dotenv import load_dotenv
from datetime import date, datetime
import qrcode # For generating QR codes
import io # For handling in-memory files (QR codes, zip)
import base64 # For generating download links
import zipfile # For creating bulk download zips
import urllib.parse # For safely encoding the URL query parameters

# Load configuration from .env file
load_dotenv()

# --- Configuration ---
DATA_FILE = "advent_messages.json"
# Using defaults based on user's config.toml for consistency, though code relies on .env
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "7623")
KID_1_NAME = os.getenv("KID_1_NAME", "Isabel")
KID_2_NAME = os.getenv("KID_2_NAME", "Sebastian")
# Streamlit typically handles environment variables as strings, so we load them as such
CALENDAR_YEAR = os.getenv("CALENDAR_YEAR", str(date.today().year))
CALENDAR_MONTH = os.getenv("CALENDAR_MONTH", "12")
HOSTING_URL_BASE = os.getenv("HOSTING_URL_BASE", "http://adventskalender2025.streamlit.app")

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


# --- QR Code Functions ---

def get_base_url():
    """Constructs the base URL for the Door Message page."""
    # Ensure the URL is clean and points to the correct page path
    base = HOSTING_URL_BASE.rstrip('/')
    return f"{base}/Door_Message"

def generate_qr_code(date_str, kid_id):
    """Generates a QR code for a specific date and kid ID, returning image bytes."""
    base_url = get_base_url()
    
    # Use urllib.parse.urlencode for safe query string construction
    params = urllib.parse.urlencode({'date': date_str, 'kid': kid_id})
    full_url = f"{base_url}?{params}"
    
    # Create QR code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to an in-memory buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer.getvalue()


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

def admin_panel(initial_data):
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

    
    # --- 1. Data Editor Section ---
    st.markdown("### 1. Message Data Editor")
    
    # Define column configurations for the editor
    column_config = {
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

    # Use st.data_editor to display and allow editing of the list of dictionaries
    edited_data = st.data_editor(
        initial_data,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="message_editor"
    )

    if st.button("Save Changes to JSON File"):
        save_data(edited_data)

    st.markdown("---")
    
    # --- 2. QR Code Generation Section ---
    st.markdown("### 2. QR Code Generation & Download")
    
    # Get active doors only
    active_doors = sorted([
        d for d in edited_data if d.get('Is_Active', False)
    ], key=lambda x: x.get('Date', '0000-00-00'))
    
    if not active_doors:
        st.info("No active doors found in the data to generate QR codes.")
        return

    door_dates = [d['Date'] for d in active_doors]
    
    # --- Bulk Download Section ---
    st.markdown("#### Bulk Download (All Active Doors)")
    
    @st.cache_data
    def generate_bulk_zip(doors):
        """Generates a zip file containing all QR codes."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for door in doors:
                date_str = door['Date']
                day = date_str.split('-')[2]
                
                # Kid 1 QR
                qr_kid1_bytes = generate_qr_code(date_str, 1)
                zf.writestr(f"Door_{day}_{KID_1_NAME}_QR.png", qr_kid1_bytes)
                
                # Kid 2 QR
                qr_kid2_bytes = generate_qr_code(date_str, 2)
                zf.writestr(f"Door_{day}_{KID_2_NAME}_QR.png", qr_kid2_bytes)
                
        return zip_buffer.getvalue()

    zip_data = generate_bulk_zip(active_doors)
    
    st.download_button(
        label=f"📦 Download ZIP ({len(active_doors) * 2} QR Codes)",
        data=zip_data,
        file_name="advent_calendar_qrcodes.zip",
        mime="application/zip",
        help="Downloads a single ZIP file containing all QR codes for all active dates and both kids."
    )
    
    st.markdown("#### Single Door View")
    
    # --- Single Door Selection and Display ---
    selected_date = st.selectbox(
        "Select Door Date to View QR Codes:",
        options=door_dates,
        index=0,
        key="selected_qr_date"
    )
    
    if selected_date:
        door_day = selected_date.split('-')[2]
        st.markdown(f"##### Door {door_day} ({selected_date})")
        
        # --- QR Code Display ---
        col_kid1, col_kid2 = st.columns(2)
        
        # Kid 1
        with col_kid1:
            st.markdown(f"###### {KID_1_NAME}'s QR Code")
            qr_kid1_bytes = generate_qr_code(selected_date, 1)
            st.image(qr_kid1_bytes, use_container_width=True)
            st.download_button(
                label=f"Download {KID_1_NAME} Door {door_day} QR",
                data=qr_kid1_bytes,
                file_name=f"Door_{door_day}_{KID_1_NAME}_QR.png",
                mime="image/png"
            )

        # Kid 2
        with col_kid2:
            st.markdown(f"###### {KID_2_NAME}'s QR Code")
            qr_kid2_bytes = generate_qr_code(selected_date, 2)
            st.image(qr_kid2_bytes, use_container_width=True)
            st.download_button(
                label=f"Download {KID_2_NAME} Door {door_day} QR",
                data=qr_kid2_bytes,
                file_name=f"Door_{door_day}_{KID_2_NAME}_QR.png",
                mime="image/png"
            )

    st.markdown("---")
    st.info(f"The QR codes point to the base URL: `{HOSTING_URL_BASE}`.")


# --- Run App ---

if __name__ == "__main__":
    # Load data here so it's only loaded once before the panel runs
    initial_data = load_data() 
    if check_password():
        admin_panel(initial_data)
    else:
        # If password check fails, the login prompt is displayed by check_password
        pass