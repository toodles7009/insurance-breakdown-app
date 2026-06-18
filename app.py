import streamlit as st
from google import genai
from google.genai import types
import random

# --- MODERN UI STYLING ---
st.set_page_config(page_title="Insurance Synthesizer", layout="centered")
st.markdown("""
    <style>
    .stApp {background-color: #f8f9fa;}
    .main-title {color: #004a99; text-align: center; font-weight: bold;}
    .cta-button {background-color: #004a99; color: white !important;}
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIC: AI ENGINE ---
def run_ai_extraction(file_bytes):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            types.Part.from_bytes(file_bytes, 'application/pdf'),
            "Extract: Annual Max, Deductibles, Coverage %. Also, write a clinical note for a dental chart."
        ]
    )
    return response.text

# --- PAGE 1: LANDING ---
def landing_page():
    st.markdown("<h1 class='main-title'>🦷 Insurance Breakdown Synthesizer</h1>", unsafe_allow_html=True)
    st.info("Clinical Note Formatter & Side-By-Side Plan Comparison")
    if st.button("Get Started", key="start"): st.session_state.page = 'signup'; st.rerun()

# --- PAGE 2: SIGNUP & AUTH ---
def signup_page():
    st.title("Secure Sign Up")
    email = st.text_input("Work Email")
    if st.button("Send Code"): st.session_state.code = 1234; st.success("Code 1234 sent!")
    code = st.text_input("Enter Code")
    if st.button("Verify"): 
        if code == "1234": st.session_state.logged_in = True; st.session_state.page = 'app'; st.rerun()

# --- PAGE 3: THE APP ---
def main_app():
    st.title("Workstation")
    tab1, tab2 = st.tabs(["📄 Parse PDF", "📊 Plan Comparison"])
    with tab1:
        file = st.file_uploader("Upload Booklet", type=["pdf"])
        if file and st.button("Run AI Extraction"):
            with st.spinner("Synthesizing..."):
                st.write(run_ai_extraction(file.getvalue()))
    with tab2:
        st.write("Compare two plans side-by-side (Feature active for subscribers).")
        st.link_button("Upgrade to Unlimited ($199/mo)", "https://buy.stripe.com/test_28E8wR67E3iz122eTFfIs01")

# --- ROUTER ---
if st.session_state.page == 'landing': landing_page()
elif st.session_state.page == 'signup': signup_page()
elif st.session_state.logged_in: main_app()
