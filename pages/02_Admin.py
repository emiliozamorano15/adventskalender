import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import base64
import os
import time
import zipfile
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

# --- Configuration (Loaded from .env) ---
DATA_FILE = "advent_messages.csv"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_password_123") # Fallback password if .env is missing
HOSTING_URL_BASE = os.getenv("HOSTING_URL_BASE", "http://localhost:8501")
KID_1_NAME = os.getenv("KID_1_NAME", "Kid 1")
KID_2_NAME = os.getenv("KID_2_NAME", "Kid 2")
MAX_DAY = 24

# The base path for the door message page
DOOR_PAGE_PATH = "/Door_Message"

def load_data():
    """Load data from CSV or create a DataFrame with columns for two kids."""
    columns = ['Day', 'Message_Kid1', 'Message_Kid2', 'Is_Active']
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Ensure all necessary columns exist for the new two-kid structure
        for col in columns:
            if col not in df.columns:
                 # Initialize missing columns, assuming existing data is in Message_Kid1 if only 'Message' was present
                if col == 'Message_Kid2' and 'Message' in df.columns:
                    df[col] = df['Message']
                elif col.startswith('Message_Kid') and 'Message' in df.columns:
                    df[col] = df['Message']
                elif col == 'Is_Active':
                    df[col] = True
                else:
                    df[col] = f"Placeholder for {col}"
        
        # Remove old 'Message' or 'QRCode_URL_Base' columns if they exist
        df = df.drop(columns=[col for col in ['Message', 'QRCode_URL_Base'] if col in df.columns], errors='ignore')
        return df[columns] # Return in the guaranteed order
        
    # Create new DataFrame if file doesn't exist
    return pd.DataFrame({
        'Day': range(1, MAX_DAY + 1),
        'Message_Kid1': [f"Secret message for {KID_1_NAME} on day {d}" for d in range(1, MAX_DAY + 1)],
        'Message_Kid2': [f"Secret message for {KID_2_NAME} on day {d}" for d in range(1, MAX_DAY + 1)],
        'Is_Active': [True] * MAX_DAY
    })

def save_data(df):
    """Save the updated DataFrame back to CSV."""
    df.to_csv(DATA_FILE, index=False)
    st.success("Messages saved successfully!")

def generate_qr_image(data_url):
    """Generates a QR code image as a PIL Image object."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(data_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def get_image_download_link(img, filename, text):
    """Generates a download link for a PIL Image."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def main():
    st.set_page_config(page_title="🔑 Settings & QR Codes", layout="wide")
    st.markdown("## 🔑 Advent Calendar Admin Panel")
    
    # Simple password protection using .env password
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.sidebar.text_input("Admin Password", type="password")
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        elif password:
            st.sidebar.error("Incorrect password.")
        st.stop()
    
    st.sidebar.success("Logged in.")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("""
        <style>
        .stApp { background-color: #f0f2f6; color: black; }
        .data-editor-container { background-color: white; padding: 10px; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # --- Main Admin UI ---
    
    df = load_data()
    
    st.header("App Configuration Status")
    st.info(f"**Hosting Base URL:** `{HOSTING_URL_BASE}`\n\n"
            f"**{KID_1_NAME} (Kid 1) URL Parameter:** `kid=1`\n\n"
            f"**{KID_2_NAME} (Kid 2) URL Parameter:** `kid=2`"
    )

    st.header("1. Edit Messages and Status")
    st.markdown('<div class="data-editor-container">', unsafe_allow_html=True)
    
    # Data Editor for editing messages
    edited_df = st.data_editor(
        df,
        column_config={
            "Day": st.column_config.NumberColumn("Day", help="Calendar Day (1-24)", disabled=True),
            "Message_Kid1": st.column_config.TextColumn(f"{KID_1_NAME}'s Message", help=f"Secret message for {KID_1_NAME}."),
            "Message_Kid2": st.column_config.TextColumn(f"{KID_2_NAME}'s Message", help=f"Secret message for {KID_2_NAME}."),
            "Is_Active": st.column_config.CheckboxColumn("Active?", help="Uncheck to temporarily disable the door, even if the date is passed.")
        },
        key="message_editor",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("💾 Save Changes"):
        save_data(edited_df)
        df = load_data() # Reload to ensure latest data is used for QR codes
        time.sleep(0.5) # Wait for file save and give visual confirmation
        st.rerun()


    st.header("2. QR Code Generation & Download")
    st.info("Two sets of QR codes are generated per day, one for each child, linking to their specific message.")

    # --- QR CODE GENERATION ---
    
    # Prepare URL templates
    url_template_kid1 = f"{HOSTING_URL_BASE}{DOOR_PAGE_PATH}?day={{day}}&kid=1"
    url_template_kid2 = f"{HOSTING_URL_BASE}{DOOR_PAGE_PATH}?day={{day}}&kid=2"


    # Create a zip file of all QR codes for easy download
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for index, row in df.iterrows():
            day = row['Day']
            
            # Kid 1 QR Code
            url1 = url_template_kid1.format(day=day)
            img1 = generate_qr_image(url1)
            img_byte_arr1 = BytesIO()
            img1.save(img_byte_arr1, format='PNG')
            zip_file.writestr(f"QR_Day_{day}_{KID_1_NAME.replace(' ', '_')}.png", img_byte_arr1.getvalue())

            # Kid 2 QR Code
            url2 = url_template_kid2.format(day=day)
            img2 = generate_qr_image(url2)
            img_byte_arr2 = BytesIO()
            img2.save(img_byte_arr2, format='PNG')
            zip_file.writestr(f"QR_Day_{day}_{KID_2_NAME.replace(' ', '_')}.png", img_byte_arr2.getvalue())


    st.download_button(
        label="📥 Download ALL 48 QR Codes (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="advent_calendar_qrcodes_duo.zip",
        mime="application/zip"
    )

    # Display individual QR codes for confirmation
    st.subheader("Individual QR Codes")
    
    # Use two columns per day to show both codes side-by-side
    
    for index, row in df.iterrows():
        day = row['Day']
        st.markdown(f"#### Day {day}")
        
        # Prepare URLs
        url1 = url_template_kid1.format(day=day)
        url2 = url_template_kid2.format(day=day)

        col_kid1, col_kid2 = st.columns(2)
        
        # KID 1 Column
        with col_kid1:
            st.caption(f"QR Code for {KID_1_NAME} (Kid 1)")
            
            # Generate and display image
            img1 = generate_qr_image(url1)
            img_buffer1 = BytesIO()
            img1.save(img_buffer1, format='PNG')
            st.image(img_buffer1.getvalue(), caption=f"URL: {url1}", use_container_width=True)
            
            # Offer download link
            filename1 = f"QR_Day_{day}_{KID_1_NAME.replace(' ', '_')}.png"
            img_download_link1 = get_image_download_link(img1, filename1, "Download PNG")
            st.markdown(img_download_link1, unsafe_allow_html=True)
            
        # KID 2 Column
        with col_kid2:
            st.caption(f"QR Code for {KID_2_NAME} (Kid 2)")
            
            # Generate and display image
            img2 = generate_qr_image(url2)
            img_buffer2 = BytesIO()
            img2.save(img_buffer2, format='PNG')
            st.image(img_buffer2.getvalue(), caption=f"URL: {url2}", use_container_width=True)
            
            # Offer download link
            filename2 = f"QR_Day_{day}_{KID_2_NAME.replace(' ', '_')}.png"
            img_download_link2 = get_image_download_link(img2, filename2, "Download PNG")
            st.markdown(img_download_link2, unsafe_allow_html=True)

if __name__ == "__main__":
    main()