import streamlit as st
from google import genai
from google.genai import types

# --- CONFIGURATION ---
st.set_page_config(page_title="Insurance Synthesizer", layout="wide")

# --- CUSTOM MODERN STYLING ---
st.markdown("""
    <style>
    .big-font {font-size:30px !important; font-weight:bold; color: #1e3a8a;}
    .card {background: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 'landing'

# --- LANDING PAGE ---
def landing_page():
    # Hero Section
    st.markdown("<p class='big-font'>Transform Insurance Booklets into Clinical Insights</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Your Practice, Optimized")
        st.write("Stop wasting hours manually reading insurance booklets. Our AI synthesizes data, formats clinical notes, and compares plans in seconds.")
        # Placeholders for modern UI visuals
        st.image("https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600", caption="Modern Dental Analytics")
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Get Started Today")
        if st.button("Log In", use_container_width=True): st.session_state.page = 'login'; st.rerun()
        if st.button("Sign Up", type="primary", use_container_width=True): st.session_state.page = 'signup'; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- AUTH & MAIN APP (Logic Remains Consistent) ---
def main_app():
    st.title("🦷 Practice Workstation")
    # ... (Insert your AI logic here as previously defined) ...
    if st.button("Log Out"): st.session_state.page = 'landing'; st.rerun()

# --- ROUTER ---
if st.session_state.page == 'landing': landing_page()
elif st.session_state.page == 'login': st.write("Login Form Placeholder")
elif st.session_state.page == 'signup': st.write("Signup Form Placeholder")
