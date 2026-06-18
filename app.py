import streamlit as st
import re
from google import genai
from google.genai import types

# --- CONFIGURATION ---
st.set_page_config(page_title="Insurance Synthesizer", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .card {background: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
    .title-text {font-size: 40px; font-weight: bold; color: #1e3a8a; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- VALIDATION LOGIC ---
def is_password_valid(password):
    if len(password) < 8: return False
    if not re.search("[a-z]", password): return False
    if not re.search("[A-Z]", password): return False
    if not re.search("[0-9]", password): return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

# --- PAGES ---
def landing_page():
    st.markdown("<p class='title-text'>Dental Insurance, Simplified.</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600", caption="Modern Dental Analytics")
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if st.button("Log In"): st.session_state.page = 'login'; st.rerun()
        if st.button("Sign Up"): st.session_state.page = 'signup'; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def auth_page(mode):
    st.title(f"{mode.capitalize()} to Your Dashboard")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if mode == "signup":
        st.caption("Password must contain: Uppercase, Lowercase, Number, and Special Character.")
        if st.button("Create Account"):
            if is_password_valid(password):
                st.success("Account Created! Redirecting...")
                st.session_state.logged_in = True; st.session_state.page = 'app'; st.rerun()
            else: st.error("Password does not meet requirements.")
    else:
        if st.button("Sign In"):
            st.session_state.logged_in = True; st.session_state.page = 'app'; st.rerun()

def app_page():
    st.title("🦷 Practice Workstation")
    file = st.file_uploader("Upload Booklet", type=["pdf"])
    if file and st.button("Run AI Extraction"):
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Part.from_bytes(file.getvalue(), 'application/pdf'), "Extract key coverage data and draft a clinical note."]
        )
        st.write(response.text)

# --- ROUTER ---
if st.session_state.page == 'landing': landing_page()
elif st.session_state.page == 'login': auth_page("login")
elif st.session_state.page == 'signup': auth_page("signup")
elif st.session_state.logged_in: app_page()
