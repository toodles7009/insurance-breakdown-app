import streamlit as st
import os
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# Initialize app
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Safe API Key check
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Please add GEMINI_API_KEY to your Streamlit Cloud Secrets.")
    st.stop()

# Initialize Client
client = genai.Client(api_key=api_key)

def main_workspace():
    st.title("🦷 Insurance Breakdown Synthesizer")
    uploaded_file = st.file_uploader("Upload Insurance Breakdown PDF", type=["pdf"])
    
    if uploaded_file and st.button("Execute AI Extraction"):
        with st.spinner("Processing document..."):
            try:
                # Read bytes and prepare part
                file_bytes = uploaded_file.getvalue()
                pdf_part = types.Part.from_bytes(data=file_bytes, mime_type='application/pdf')
                
                # Using gemini-2.0-flash, which is fully supported on the v1 production path
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        pdf_part, 
                        "Extract annual max, deductibles, coverage percentages, and critical clauses."
                    ]
                )
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    main_workspace()
