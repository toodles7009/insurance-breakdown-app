import streamlit as st
import sqlite3
import bcrypt
import google.generativeai as genai
import os

# ==========================================
# 1. INITIALIZATION & DATABASE SETUP
# ==========================================
st.set_page_config(page_title="Insurance Breakdown Synthesizer", layout="wide")

# Connect to local SQLite database to track office accounts and upload limits
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

# Configure Google Gemini API (Reads from your Streamlit Secrets or Environment Variables)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
elif os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
else:
    st.warning("Gemini API Key missing. Please add it to your secrets or environment variables.")

# STRIPE CONFIGURATION (Replace with your actual Test Mode Link from your Stripe dashboard)
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/test_28E8wR67E3iz122eTFfIs01"

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ==========================================
# 2. AUTHENTICATION INTERFACE (LOGIN/SIGNUP)
# ==========================================
def auth_screen():
    st.title("🦷 Insurance Breakdown Synthesizer")
    st.subheader("Login or Create an Account for Your Practice")
    
    tab1, tab2 = st.tabs(["Sign In", "Register Practice"])
    
    with tab1:
        login_user = st.text_input("Username / Email", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            cursor.execute("SELECT password, upload_count, is_subscribed FROM offices WHERE username=?", (login_user,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(login_pass.encode('utf-8'), result[0]):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    with tab2:
        reg_user = st.text_input("Choose Username / Email", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account"):
            if reg_user and reg_pass:
                hashed = bcrypt.hashpw(reg_pass.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute("INSERT INTO offices (username, password) VALUES (?, ?)", (reg_user, hashed))
                    conn.commit()
                    st.success("Account created successfully! Please sign in.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")
            else:
                st.error("Please fill out all fields.")

# ==========================================
# 3. MAIN APPLICATION WORKSPACE
# ==========================================
def main_workspace():
    # Fetch current user limits
    cursor.execute("SELECT upload_count, is_subscribed FROM offices WHERE username=?", (st.session_state.username,))
    upload_count, is_subscribed = cursor.fetchone()
    
    # Sidebar Header & Navigation
    st.sidebar.title("🏥 Practice Dashboard")
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    
    if not is_subscribed:
        st.sidebar.info(f"Free Trial Usage: {upload_count} / 5 Free Uploads")
    else:
        st.sidebar.success("✨ Premium Account Active")
        
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    # ---- HARD PAYWALL LOGIC ----
    if upload_count >= 5 and not is_subscribed:
        st.error("🛑 **Trial Limit Reached**")
        st.write("Your practice has exhausted its 5 free insurance breakdown trial parsing credits.")
        st.write("Upgrade now to unlock unlimited parsing, the clinical notes generator, and side-by-side matrices.")
        
        # Big call to action button linking to Stripe sandbox link
        st.link_button("⭐ Upgrade to Unlimited ($199/mo)", STRIPE_PAYMENT_LINK, type="primary")
        return

    # Application Tabs
    app_tab1, app_tab2 = st.tabs(["📄 Parse Insurance Booklet", "📊 Dual-Plan Comparison Matrix"])
    
    # --- TAB 1: PARSING ENGINE ---
    with app_tab1:
        st.header("Upload Insurance Breakdown PDF")
        uploaded_file = st.file_uploader("Drop the full breakdown document or booklet here", type=["pdf"])
        
        if uploaded_file is not None:
            if st.button("Execute AI Extraction"):
                with st.spinner("Reading the document and extracting clauses..."):
                    try:
                        # Setup the AI model
                        model = genai.GenerativeModel("gemini-1.5-flash-latest")
                        
                        # Convert uploaded file to bytes for the API
                        file_bytes = uploaded_file.read()
                        
                        prompt = """
                        You are an expert dental billing specialist. Analyze this dental insurance breakdown PDF and extract the following:
                        1. Annual Maximum and remaining balance if listed.
                        2. Individual and Family Deductibles.
                        3. Preventative, Basic, and Major coverage percentages.
                        4. Specific critical clauses: 
                           - Missing Tooth Clause (Is a replacement tooth covered if the tooth was missing before plan activation?)
                           - Molar Downgrades (Are posterior composite restorations downgraded to silver/amalgam allowances?)
                           - Waiting periods for major work.
                        Provide a clean markdown summary followed by a single condensed clinical note paragraph for dental software logs.
                        """
                        
                        # Pass the PDF directly into Gemini 1.5 Pro
                        response = model.generate_content([
                            {"mime_type": "application/pdf", "data": file_bytes},
                            prompt
                        ])
                        
                        # Increment upload counter in local database
                        new_count = upload_count + 1
                        cursor.execute("UPDATE offices SET upload_count=? WHERE username=?", (new_count, st.session_state.username))
                        conn.commit()
                        
                        st.success("Extraction Complete!")
                        st.markdown(response.text)
                        
                        # Force refresh to update sidebar tracker badge
                        st.button("Update Dashboard Balance")
                        
                    except Exception as e:
                        st.error(f"An error occurred during parsing: {e}")

    # --- TAB 2: SIDE-BY-SIDE MATRIX ---
    with app_tab2:
        st.header("Dual-Plan Strategy Matrix")
        st.write("Select two extracted plans to compare patient out-of-pocket exposure side-by-side.")
        
        # Placeholder layout for feature visualization
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Select Baseline Plan", ["Delta Dental Premier PPO (Example)", "MetLife PDP Gold (Example)"])
        with col2:
            st.selectbox("Select Alternative Plan", ["Cigna Radius Savings (Example)", "Aetna Dental Access (Example)"])
            
        if st.button("Run Comparison Analysis"):
            st.info("Upgrade to a Premium tier to populate and customize live comparison matrices.")

# ==========================================
# 4. ROUTER RUNNER
# ==========================================
if __name__ == "__main__":
    if not st.session_state.logged_in:
        auth_screen()
    else:
        main_workspace()
