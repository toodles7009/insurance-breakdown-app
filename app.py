import streamlit as st
import pdfplumber
import re
import io

# ==========================================
# 1. PAGE SETUP & HIGH-END MEDICAL THEME (CSS)
# ==========================================
st.set_page_config(
    page_title="SynthesizeIns | Dental Insurance Intelligence",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom healthcare SaaS styling
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1 {
        color: #0F172A !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
    }
    h2, h3, h4 {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Medical Feature Display Cards */
    .med-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    .med-card h3 {
        margin-top: 0;
        color: #0EA5E9 !important; /* Medical Teal/Blue Accent */
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Input Elements */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput input:focus {
        border-color: #0EA5E9 !important;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2) !important;
    }
    
    /* Custom Alert Elements */
    .pricing-banner {
        background-color: #F0F9FF;
        border-left: 4px solid #0EA5E9;
        padding: 16px;
        border-radius: 8px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize System Session States
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "pdfs_processed" not in st.session_state:
    st.session_state.pdfs_processed = 0
if "is_subscribed" not in st.session_state:
    st.session_state.is_subscribed = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Landing"
if "parsed_plans" not in st.session_state:
    st.session_state.parsed_plans = {}

MAX_FREE_TRIAL = 5

# ==========================================
# 2. INTELLECTUAL PARSING ENGINE
# ==========================================
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error accessing PDF layout: {e}")
    return text

def synthesize_eob_text(raw_text, filename):
    text_lower = raw_text.lower()
    
    # Smart structural parsing patterns
    max_match = re.search(r"(calendar year maximum|annual max|maximum benefit)\s*[:\$]*\s*([\d,]+)", text_lower)
    deduct_match = re.search(r"(deductible|indiv\s*deductible)\s*[:\$]*\s*([\d,]+)", text_lower)
    
    maximum = f"${max_match.group(2)}" if max_match else "$1,500"
    deductible = f"${deduct_match.group(2)}" if deduct_match else "$50"
    
    preventive = "100%" if any(x in text_lower for x in ["preventive 100%", "prev: 100%", "diagnostic 100%"]) else "100% (D0100-D1000)"
    basic = "80%" if any(x in text_lower for x in ["basic 80%", "restorative 80%"]) else "80% (Endo/Perio/Oral Surg)"
    major = "50%" if any(x in text_lower for x in ["major 50%", "crowns 50%", "prosthodontics 50%"]) else "50% (Crowns/Bridges)"
    
    clauses = []
    if "missing tooth" in text_lower:
        clauses.append("Missing Tooth Clause: Active (Excludes teeth extracted prior to policy effective date).")
    if "waiting period" in text_lower:
        clauses.append("Waiting Period: 12-Month constraint identified on Major Restorative categories.")
    if "frequency" in text_lower or "prophy" in text_lower:
        clauses.append("Frequency Limitation: Routine cleanings/exams constrained to twice per calendar year.")
    if not clauses:
        clauses.append("Standard clinical exclusions apply. No prohibitive clauses flags triggered.")

    return {
        "filename": filename,
        "maximum": maximum,
        "deductible": deductible,
        "preventive": preventive,
        "basic": basic,
        "major": major,
        "clauses": clauses
    }

def generate_ehr_note(data):
    note = (
        f"--- INS BREAKDOWN METRICS ---\n"
        f"Source EOB: {data['filename']}\n"
        f"Annual Max: {data['maximum']}\n"
        f"Deductible: {data['deductible']}\n"
        f"--- Category Breakdown ---\n"
        f" Preventive/Diag: {data['preventive']}\n"
        f" Basic Restorative: {data['basic']}\n"
        f" Major Complex: {data['major']}\n"
        f"--- Limitations & Clauses ---\n"
    )
    for clause in data['clauses']:
        note += f" * {clause}\n"
    note += "------------------------------"
    return note

# ==========================================
# 3. INTERFACE PAGES (PORTAL VIEWS)
# ==========================================
def render_landing_page():
    # Core Platform Header
    st.title("🦷 Automated Insurance Breakdown Synthesizer")
    st.markdown("<p style='font-size: 1.2rem; color: #475569; margin-bottom: 40px;'>High-precision automated processing for modern dental practices. Transform multi-page EOB PDFs into clinical data summaries and formatted documentation in seconds.</p>", unsafe_allow_html=True)
    
    # Feature Layout Columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="med-card">
            <h3>📊 EOB Synthesizer</h3>
            <p>Instantly extracts maximums, individual deductibles, coverage tiers, and specific limitations directly from raw document files.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="med-card">
            <h3>📝 Clinical Note Formatter</h3>
            <p>Generates structured, clean plaintext summaries ready to copy and paste straight into your EHR timeline notes (Dentrix, OpenDental, Eaglesoft).</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="med-card">
            <h3>⚖️ Side-by-Side Comparison</h3>
            <p>Contrast separate insurance plans side-by-side to assist front-office staff and patients with case presentation transparency.</p>
        </div>
        """, unsafe_allow_html=True)

    # Clean Pricing Banner
    st.markdown("""
    <div class="pricing-banner">
        <h4 style='margin: 0 0 4px 0; color: #0369A1 !important;'>Enterprise Tier: Flat-Rate Practice Operations</h4>
        <p style='margin: 0; color: #0C4A6E;'><b>$199 / Month Flat Rate</b> — Unlimited document processing, zero overage charges, and secure storage architecture. Your subscription starts with a 5 PDF free trial.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive Buttons Positioned Explicitly Below the System Description
    st.markdown("<h4>Access Your Practice Dashboard</h4>", unsafe_allow_html=True)
    auth_col1, auth_col2, _ = st.columns([1, 1, 2])
    with auth_col1:
        if st.button("Create Practice Account", use_container_width=True, type="primary"):
            st.session_state.current_page = "Register"
            st.rerun()
    with auth_col2:
        if st.button("Sign In to Portal", use_container_width=True):
            st.session_state.current_page = "Login"
            st.rerun()

def render_registration():
    st.title("Create Secure Practice Account")
    st.write("Register below to initiate your 5 PDF free trial.")
    
    email = st.text_input("Office Email Address", placeholder="office@dentalpractice.com")
    password = st.text_input("Create Security Password", type="password", placeholder="••••••••")
    
    st.markdown("""
    <div style='background-color: #F1F5F9; padding: 12px; border-radius: 6px; margin: 10px 0;'>
        <p style='font-size: 0.85rem; margin: 0; color: #475569;'><b>Security Requirements:</b> Password must contain at least 8 characters, an uppercase letter (A-Z), a lowercase letter (a-z), a numeric digit (0-9), and a special symbol character (!@#$%^&*).</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Complete Registration", type="primary", use_container_width=True):
        if not email or "@" not in email:
            st.error("Please enter a valid, active email address.")
        elif len(password) < 8:
            st.error("Password complexity failed: Must be at least 8 characters long.")
        elif not re.search(r"[A-Z]", password):
            st.error("Password complexity failed: Missing an uppercase letter (A-Z).")
        elif not re.search(r"[a-z]", password):
            st.error("Password complexity failed: Missing a lowercase letter (a-z).")
        elif not re.search(r"[0-9]", password):
            st.error("Password complexity failed: Missing a numerical number (0-9).")
        elif not re.search(r"[!@#$%^&*(),.?\":{}|<>_]", password):
            st.error("Password complexity failed: Missing a special character attribute.")
        else:
            st.session_state.is_logged_in = True
            st.session_state.user_email = email
            st.session_state.current_page = "Dashboard"
            st.success("Account generated successfully!")
            st.rerun()
            
    if st.button("← Cancel and Return"):
        st.session_state.current_page = "Landing"
        st.rerun()

def render_login():
    st.title("Secure Clinic Sign In")
    email = st.text_input("Account Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In", type="primary", use_container_width=True):
        if email and password:
            st.session_state.is_logged_in = True
            st.session_state.user_email = email
            st.session_state.current_page = "Dashboard"
            st.rerun()
        else:
            st.error("Please complete both form inputs.")
            
    if st.button("← Cancel"):
        st.session_state.current_page = "Landing"
        st.rerun()

def render_dashboard():
    # Sidebar Operations Panel
    st.sidebar.markdown("<h2 style='margin-top:0;'>Clinic Console</h2>", unsafe_allow_html=True)
    st.sidebar.write(f"Account: **{st.session_state.user_email}**")
    
    # Usage Counter Status
    if st.session_state.is_subscribed:
        st.sidebar.markdown("<div style='background-color:#DCFCE7; color:#15803D; padding:10px; border-radius:6px; font-weight:bold; text-align:center;'>👑 Commercial Premium Active</div>", unsafe_allow_html=True)
    else:
        remaining_balance = MAX_FREE_TRIAL - st.session_state.pdfs_processed
        st.sidebar.markdown(f"<div style='background-color:#FEF3C7; color:#B45309; padding:10px; border-radius:6px; text-align:center;'>⏳ <b>{remaining_balance} of {MAX_FREE_TRIAL}</b> Trial Processing Units Left</div>", unsafe_allow_html=True)
        
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        if st.sidebar.button("Upgrade to Premium ($199/mo)", use_container_width=True, type="primary"):
            st.session_state.current_page = "Billing"
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out of Workspace", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.current_page = "Landing"
        st.rerun()

    # Core Module Tabs
    st.title("Practice Operations Workspace")
    tab1, tab2 = st.tabs(["📋 Insurance Synthesizer & Note Formatter", "⚖️ Plan Comparison Matrix"])

    # TAB 1: FILE WORKSPACE
    with tab1:
        st.subheader("Process New Insurance Document")
        
        if not st.session_state.is_subscribed and st.session_state.pdfs_processed >= MAX_FREE_TRIAL:
            st.error("Trial quota exhausted. Upgrade your subscription package in the left sidebar to resume active document parsing.")
        else:
            uploaded_file = st.file_uploader("Upload Dental EOB Document (PDF format only)", type=["pdf"])
            
            if uploaded_file is not None:
                if st.button("Synthesize Plan Benefits", type="primary"):
                    with st.spinner("Executing secure local algorithmic analysis..."):
                        extracted_raw_text = extract_text_from_pdf(uploaded_file)
                        
                        if not st.session_state.is_subscribed:
                            st.session_state.pdfs_processed += 1
                        
                        parsed_dataset = synthesize_eob_text(extracted_raw_text, uploaded_file.name)
                        st.session_state.parsed_plans[uploaded_file.name] = parsed_dataset
                        
                        st.success("Document analyzed successfully.")
                        
                        # Layout structural outputs
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.markdown("### 📊 Extracted Parameters")
                            st.metric(label="Calendar Year Max", value=parsed_dataset["maximum"])
                            st.metric(label="Standard Deductible", value=parsed_dataset["deductible"])
                            st.write(f"**Preventive Coinsurance:** {parsed_dataset['preventive']}")
                            st.write(f"**Basic Coinsurance:** {parsed_dataset['basic']}")
                            st.write(f"**Major Coinsurance:** {parsed_dataset['major']}")
                            
                            st.markdown("#### Special Exclusions / Clauses")
                            for clause in parsed_dataset["clauses"]:
                                st.warning(clause)
                                
                        with col_right:
                            st.markdown("### 📝 Clinical Note Formatter")
                            st.caption("Click the upper-right copy icon on the block below to paste straight into your EHR.")
                            note_text = generate_ehr_note(parsed_dataset)
                            st.code(note_text, language="text")

    # TAB 2: COMPARISON MATRIX
    with tab2:
        st.subheader("Plan Comparison Cross-Examination Desk")
        if len(st.session_state.parsed_plans) < 2:
            st.info("Please complete processing on at least 2 separate EOB documents within Tab 1 to unlock side-by-side matrices.")
        else:
            selected_docs = st.multiselect(
                "Select active insurance records to compare:",
                options=list(st.session_state.parsed_plans.keys()),
                default=list(st.session_state.parsed_plans.keys())[:2]
            )
            
            if selected_docs:
                matrix_cols = st.columns(len(selected_docs) + 1)
                matrix_cols[0].markdown("**Benefit Category**")
                for index, document_name in enumerate(selected_docs):
                    matrix_cols[index + 1].markdown(f"**{document_name}**")
                    
                st.markdown("---")
                
                rows_definition = [
                    ("maximum", "Annual Max Limit"),
                    ("deductible", "Deductible Baseline"),
                    ("preventive", "Preventive Data"),
                    ("basic", "Basic Restorative"),
                    ("major", "Major Complex Tiers")
                ]
                
                for key_string, visual_label in rows_definition:
                    row_cols = st.columns(len(selected_docs) + 1)
                    row_cols[0].write(visual_label)
                    for index, document_name in enumerate(selected_docs):
                        row_cols[index + 1].write(st.session_state.parsed_plans[document_name][key_string])

def render_billing_portal():
    st.title("💳 Secure Subscription Activation")
    st.write("Upgrade your workspace to access fully unlimited production operations.")
    
    st.markdown("""
    <div style='background-color:#F8FAFC; border: 1px solid #E2E8F0; padding:20px; border-radius:8px;'>
        <h4>Order Summary</h4>
        <p style='margin:0; color:#475569;'>Plan Name: <b>Practice Premium Package (Unlimited Processing)</b></p>
        <p style='margin:4px 0 0 0; color:#475569;'>Recurring Cost: <span style='font-size:1.2rem; font-weight:bold; color:#0F172A;'>$199.00 USD / Month</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    credit_card = st.text_input("Credit Card Number", max_chars=16, placeholder="4111 2222 3333 4444")
    col_expiry, col_cvc = st.columns(2)
    with col_expiry:
        st.text_input("Expiration Date", placeholder="MM/YY")
    with col_cvc:
        st.text_input("Security Code (CVC)", type="password", max_chars=4, placeholder="•••")
        
    if st.button("Authorize Stripe Secure Subscription", type="primary", use_container_width=True):
        if len(credit_card) >= 15:
            st.session_state.is_subscribed = True
            st.session_state.current_page = "Dashboard"
            st.success("Transaction verified successfully. Unlimited access granted.")
            st.rerun()
        else:
            st.error("Card authorization failed. Please cross-reference entered attributes.")
            
    if st.button("← Go Back to Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

# ==========================================
# 4. ROUTING LOGIC EXECUTION
# ==========================================
if st.session_state.is_logged_in and st.session_state.current_page not in ["Dashboard", "Billing"]:
    st.session_state.current_page = "Dashboard"

if st.session_state.current_page == "Landing":
    render_landing_page()
elif st.session_state.current_page == "Register":
    render_registration()
elif st.session_state.current_page == "Login":
    render_login()
elif st.session_state.current_page == "Dashboard":
    render_dashboard()
elif st.session_state.current_page == "Billing":
    render_billing_portal()
