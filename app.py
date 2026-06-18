import streamlit as st
import os
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# Initialize the client without extra options to avoid conflicts
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def main_workspace():
    st.header("Upload Insurance Breakdown PDF")
    uploaded_file = st.file_uploader("Drop the PDF here", type=["pdf"])
    
    if uploaded_file and st.button("Execute AI Extraction"):
        with st.spinner("Processing..."):
            try:
                # Use the 'gemini-1.5-flash' model directly
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=uploaded_file.getvalue(), 
                            mime_type='application/pdf'
                        ),
                        "Extract annual max, deductibles, coverage percentages, and critical clauses."
                    ]
                )
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main_workspace()
