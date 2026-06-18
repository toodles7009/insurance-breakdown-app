import streamlit as st
import os
import sqlite3
import bcrypt
import base64
from google import genai

# ==========================================
# 1. INITIALIZATION
# ==========================================
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Database setup
conn = sqlite3.connect("practice_vault.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS offices (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, upload_count INTEGER DEFAULT 0, is_subscribed INTEGER DEFAULT 0)''')
conn.commit()

# Initialize Client using the new SDK
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Gemini API Key missing.")
    st.stop()

# Correct initialization for google-genai
client = genai.Client(api_key=api_key)

# ==========================================
# 2. MAIN WORKSPACE
# ==========================================
def main_workspace():
    # ... (Keep your auth and sidebar logic here)
    
    app_tab1, app_tab2 = st.tabs(["📄 Parse Insurance Booklet", "📊 Dual-Plan Comparison Matrix"])
    
    with app_tab1:
        st.header("Upload Insurance Breakdown PDF")
        uploaded_file = st.file_uploader("Drop the PDF here", type=["pdf"])
        
        if uploaded_file is not None:
            if st.button("Execute AI Extraction"):
                with st.spinner("Extracting clauses..."):
                    try:
                        file_bytes = uploaded_file.getvalue()
                        
                        # Correct call for the new SDK
                        # Note: We pass data directly to contents
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=[
                                {"mime_type": "application/pdf", "data": file_bytes},
                                "Analyze this dental insurance breakdown PDF and extract: Annual Max, Deductibles, Coverage percentages, and critical clauses."
                            ]
                        )
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    # Ensure your auth logic triggers this
    main_workspace()
