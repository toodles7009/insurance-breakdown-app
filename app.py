import streamlit as st
import sqlite3
import bcrypt
from google import genai
from google.genai import types

# 1. SETUP & DATABASE
st.set_page_config(page_title="Insurance Synthesizer", layout="wide")
conn = sqlite3.connect("practice_vault.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS offices 
                  (username TEXT PRIMARY KEY, password TEXT, upload_count INTEGER DEFAULT 0, is_subscribed INTEGER DEFAULT 0)''')
conn.commit()

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None

# 2. INTERFACE FUNCTIONS
def main_workspace():
    # Sidebar: Subscription & Logout
    cursor.execute("SELECT upload_count, is_subscribed FROM offices WHERE username=?", (st.session_state.username,))
    row = cursor.fetchone()
    count, sub = row
    
    st.sidebar.title("🏥 Practice Dashboard")
    st.sidebar.write(f"Usage: {count}/5 Free Trial")
    if not sub:
        st.sidebar.link_button("⭐ Upgrade to Unlimited ($199/mo)", "https://buy.stripe.com/test_28E8wR67E3iz122eTFfIs01")
    
    # Tabs
    tab1, tab2 = st.tabs(["📄 Parse & Clinical Note", "📊 Dual-Plan Comparison"])
    
    with tab1:
        st.header("Upload Insurance Breakdown")
        file = st.file_uploader("Upload PDF", type=["pdf"])
        if file and st.button("Extract & Format"):
            if count >= 5 and not sub:
                st.error("Trial ended. Please subscribe.")
            else:
                with st.spinner("Analyzing..."):
                    bytes_data = file.getvalue()
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[
                            types.Part.from_bytes(bytes_data, 'application/pdf'),
                            "Extract coverage (Max, Ded, %), Clauses (Missing tooth, Molar), and create a concise clinical note for software logs."
                        ]
                    )
                    st.markdown(response.text)
                    cursor.execute("UPDATE offices SET upload_count = upload_count + 1 WHERE username=?", (st.session_state.username,))
                    conn.commit()

    with tab2:
        st.header("Side-by-Side Comparison")
        col1, col2 = st.columns(2)
        p1 = col1.text_area("Baseline Plan Data")
        p2 = col2.text_area("Alternative Plan Data")
        if st.button("Compare Out-of-Pocket"):
            st.info("Comparison analysis feature active for subscribers.")

# 3. ROUTER
if not st.session_state.logged_in:
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()
else:
    main_workspace()
