import streamlit as st
import os
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# ==========================================
# 1. INITIALIZATION & DATABASE SETUP
# ==========================================
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Connect to database
conn = sqlite3.connect("practice_vault.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS offices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        upload_count INTEGER DEFAULT 0,
        is_subscribed INTEGER DEFAULT 0
    )
''')
conn.commit()

# Initialize the new Google GenAI Client
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Gemini API Key missing. Please check your secrets.")
    st.stop()

# Initialize client
client = genai.Client(api_key=api_key)

# STRIPE CONFIGURATION
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/test_28E8wR67E3iz122eTFfIs01"

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None

# [Include auth_screen() and main_workspace() functions as you had them, 
# BUT update the Extraction logic inside main_workspace as shown below]

# --- UPDATED EXTRACTION LOGIC FOR TAB 1 ---
if uploaded_file is not None:
    if st.button("Execute AI Extraction"):
        with st.spinner("Reading the document..."):
            try:
                # Convert PDF to bytes
                file_bytes = uploaded_file.read()
                
                # New SDK format for file uploads
                prompt = "Analyze this dental insurance breakdown PDF and extract coverage, deductibles, and clauses..."
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        types.Part.from_data(data=file_bytes, mime_type="application/pdf"),
                        prompt
                    ]
                )
                
                # Update DB and show result
                new_count = upload_count + 1
                cursor.execute("UPDATE offices SET upload_count=? WHERE username=?", (new_count, st.session_state.username))
                conn.commit()
                
                st.success("Extraction Complete!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Extraction failed: {e}")
