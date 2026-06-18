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
client = genai.Client(api_key=api_key)

# STRIPE CONFIGURATION
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/test_28E8wR67E3iz122eTFfIs01"

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None

# ==========================================
# 2. AUTHENTICATION & WORKSPACE FUNCTIONS
# ==========================================
def auth_screen():
    st.title("🦷 Insurance Breakdown Synthesizer")
    tab1, tab2 = st.tabs(["Sign In", "Register Practice"])
    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            cursor.execute("SELECT password FROM offices WHERE username=?", (login_user,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(login_pass.encode('utf-8'), result[0]):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else: st.error("Invalid credentials.")
    with tab2:
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account"):
            hashed = bcrypt.hashpw(reg_pass.encode('utf-8'), bcrypt.gensalt())
            try:
                cursor.execute("INSERT INTO offices (username, password) VALUES (?, ?)", (reg_user, hashed))
                conn.commit()
                st.success("Account created!")
            except: st.error("Username exists.")

def main_workspace():
    cursor.execute("SELECT upload_count, is_subscribed FROM offices WHERE username=?", (st.session_state.username,))
    upload_count, is_subscribed = cursor.fetchone()
    
    st.sidebar.title("🏥 Practice Dashboard")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    app_tab1, app_tab2 = st.tabs(["📄 Parse Insurance Booklet", "📊 Dual-Plan Comparison Matrix"])
    
    with app_tab1:
        st.header("Upload Insurance Breakdown PDF")
        uploaded_file = st.file_uploader("Drop the PDF here", type=["pdf"])
        
        if uploaded_file is not None:
            if st.button("Execute AI Extraction"):
                with st.spinner("Extracting clauses..."):
                    try:
                        file_bytes = uploaded_file.read()
                        prompt = "Extract annual max, deductibles, preventative/basic/major coverage, and critical clauses."
                        
                        response = client.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=[
                                types.Part.from_data(data=file_bytes, mime_type="application/pdf"),
                                prompt
                            ]
                        )
                        st.markdown(response.text)
                        
                        cursor.execute("UPDATE offices SET upload_count=? WHERE username=?", (upload_count + 1, st.session_state.username))
                        conn.commit()
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    if not st.session_state.logged_in: auth_screen()
    else: main_workspace()
