# 🎄 Personalized Advent Calendar Portal (Duo Edition)

This Streamlit application creates a dynamic, personalized, and time-gated Advent Calendar experience for two children. It allows parents (admins) to customize daily secret messages, generate unique QR codes for each door, and ensure messages are only revealed on or after the specified calendar day.✨ 
## Features
- Two-Kid Personalization: Supports two distinct sets of messages (Message_Kid1 and Message_Kid2) managed via the same data file.
- Time-Gating: Doors can only be opened on or after the day set in the URL (e.g., Day 5 can only be opened on or after the 5th of the configured month/year).
- Admin Panel (Password Protected): An interface for editing messages, toggling door activity, and generating QR codes.
- QR Code Generation: Generates individual QR codes for every day for both children, packaged in a downloadable ZIP file.
- Flexible Calendar Dates: The calendar month and year are configurable via the .env file, allowing testing outside of December.🛠️ 

## Prerequisites
You need Python installed on your system.
1. Python 3.8+
2. Required Python packages (listed in requirements.txt).
3. 
## 🚀 Setup and Installation
Follow these steps to get your Advent Calendar running locally.

### 1. Install Dependencies

First, ensure you have all necessary packages installed.

```
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The core settings for the application are controlled by the .env file. You must set these values according to your needs. <br> 
`.env`
```
# --- GENERAL CONFIGURATION ---
ADMIN_PASSWORD="supersecretpassword123_new"

# Set the base URL of your deployed Streamlit app
HOSTING_URL_BASE="http://localhost:8501"

# --- CALENDAR DATE CONFIGURATION (MUST BE INTEGERS) ---
# Current configuration allows testing in November 2025 up to day 25
CALENDAR_YEAR=2025
CALENDAR_MONTH=11
MAX_DAY=25

# --- KID CONFIGURATION ---
# Define the names for Kid 1 and Kid 2.
KID_1_NAME="Isabel"
KID_2_NAME="Sebastian"
```

**Key Configuration Notes:**
- ADMIN_PASSWORD: Choose a strong password to protect the Admin Panel.
- HOSTING_URL_BASE: Set this to the URL where your Streamlit app is accessible. For local development, http://localhost:8501 is standard.
- CALENDAR_MONTH: Set this to 12 for a real Advent Calendar run, or 11 (or your current month) for testing the time-gating.
- Kid IDs: The URL logic uses kid=1 and kid=2. The names (KID_1_NAME / KID_2_NAME) are for display purposes only. 

### 3. Run the Application
   
Start the Streamlit application from your terminal:
```
streamlit run 00_Main_Portal.py
```

## 📝 Usage

### Accessing the Admin Panel

1. Navigate to the Admin page (often available via the sidebar menu under Admin).
2. Enter the ADMIN_PASSWORD defined in your .env file.
3. Edit Messages: Use the table editor to customize the Message_Kid1 and Message_Kid2 columns for each day.
4. Save: Click "💾 Save Changes" to update the advent_messages.csv file.

### Generating and Using QR Codes

1. In the Admin Panel, navigate to the "2. QR Code Generation & Download" section.
2. Click "📥 Download ALL 48 QR Codes (ZIP)" to get a single file containing all codes (24 days * 2 kids).
3. The QR code files are named clearly, e.g., QR_Day_5_Isabel.png and QR_Day_5_Sebastian.png.
4. Print and attach the correct QR codes to the corresponding calendar doors.

### Manual Door Access (For Testing)

To manually test a door message, use the following URL format, replacing [BASE_URL] with your HOSTING_URL_BASE, [DAY] with the door number, and [KID_ID] with the recipient's numeric ID (1 or 2).

Format:

```
[BASE_URL]/Door_Message?day=[DAY]&kid=[KID_ID]
```

Example (Day 5 for Sue/Kid 1):

```
http://localhost:8501/Door_Message?day=5&kid=1
````
