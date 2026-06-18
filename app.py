import streamlit as st
import os
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# ==========================================
# 1. INITIALIZATION & SAFETY
# ==========================================
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Safe API Key retrieval
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to your Streamlit Cloud Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Database Setup
conn = sqlite3.connect("practice_vault.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS offices 
                  (username TEXT PRIMARY KEY, password TEXT, upload_count INTEGER DEFAULT 0, is_subscribed INTEGER DEFAULT 0)''')
conn.commit()

# ==========================================
# 2. MAIN APPLICATION
# ==========================================
def main_workspace():
    st.title("🦷 Insurance Breakdown Synthesizer")
    
    # Simple File Uploader
    uploaded_file = st.file_uploader("Upload Insurance Breakdown PDF", type=["pdf"])
    
    if uploaded_file and st.button("Execute AI Extraction"):
        with st.spinner("Processing document..."):
            try:
                # Modern data handling
                file_bytes = uploaded_file.getvalue()
                pdf_part = types.Part.from_bytes(data=file_bytes, mime_type='application/pdf')
                
                # Model request
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        pdf_part, 
                        "Extract annual max, deductibles, coverage percentages, and critical clauses. Include a clinical note for software."
                    ]
                )
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    main_workspace()
