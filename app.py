import streamlit as st
import os
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# ==========================================
# 1. INITIALIZATION
# ==========================================
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Database setup
conn = sqlite3.connect("practice_vault.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS offices 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, 
                   upload_count INTEGER DEFAULT 0, is_subscribed INTEGER DEFAULT 0)''')
conn.commit()

# Initialize Client with stable v1 API version
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Gemini API Key missing. Please check your secrets.")
    st.stop()
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

# ==========================================
# 2. APPLICATION LOGIC
# ==========================================
def main_workspace():
    # Placeholder for auth check logic
    if "username" not in st.session_state: st.session_state.username = "demo_user"
    
    st.header("Upload Insurance Breakdown PDF")
    uploaded_file = st.file_uploader("Drop the PDF here", type=["pdf"])
    
    # Logic is now correctly nested inside this function scope
    if uploaded_file is not None:
        if st.button("Execute AI Extraction"):
            with st.spinner("Processing with Gemini..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    pdf_part = types.Part.from_bytes(data=file_bytes, mime_type='application/pdf')
                    prompt = "Extract annual max, deductibles, coverage percentages, and critical clauses."
                    
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[pdf_part, prompt]
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    main_workspace()
