import streamlit as st
from chain_utils import get_file_hash, anchor_to_polygon
from aadhaar_utils import create_signing_request_MOCK
import time

# ---------------------------------------------------------
# 1. PAGE CONFIG & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="SiteSign Pro",
    page_icon="🛡️",
    layout="centered"
)

# Initialize Session State (To remember where we are)
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'signed' not in st.session_state:
    st.session_state.signed = False

# ---------------------------------------------------------
# 2. CSS STYLING (High Contrast Fix)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 1. Force the main background to a neutral light gray */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* 2. Fix the Header Card (White Background, Black Text) */
    .header-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 24px;
        border-bottom: 4px solid #3b82f6; /* Blue bottom border */
    }
    
    /* 3. Force Text Colors inside the Header to be Dark */
    .header-card h2 {
        color: #1e293b !important;
        margin: 0;
    }
    .header-card p {
        color: #64748b !important;
        margin: 5px 0 0 0;
    }

    /* 4. Fix the Success/Certificate Box */
    .success-box {
        background-color: #ffffff;
        border: 2px solid #10b981;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1);
    }
    .success-box h2 {
        color: #059669 !important; /* Dark Green */
    }
    .success-box p, .success-box div {
        color: #374151 !important; /* Dark Gray */
    }

    /* 5. Fix Streamlit's Native Widgets (Input fields) */
    .stTextInput label, .stNumberInput label, .stTextArea label, .stCameraInput label {
        color: #1e293b !important; /* Dark Blue-Gray */
        font-weight: 600;
    }
    
    /* 6. Buttons */
    div.stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #2563eb;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="header-card">
    <h2>🛡️ SiteSign Pro</h2>
    <p>Legal Payment Protection for Contractors</p>
</div>
""", unsafe_allow_html=True)

# Progress Bar
if st.session_state.step == 1:
    st.progress(33)
elif st.session_state.step == 2:
    st.progress(66)
else:
    st.progress(100)

# ---------------------------------------------------------
# 4. STEP 1: CAPTURE
# ---------------------------------------------------------
if st.session_state.step == 1:
    st.markdown("### 📸 Step 1: Capture Details")
    
    with st.container():
        photo = st.camera_input("Take a photo of the site")
        desc = st.text_area("Description of Work", placeholder="e.g. Extra plumbing for kitchen island...")
        cost = st.number_input("Agreed Extra Cost (₹)", min_value=0, step=500)
        client_phone = st.text_input("Client Phone Number", placeholder="9876543210")

        if photo and desc and cost > 0 and client_phone:
            if st.button("Next: Verify & Sign ➡️", type="primary"):
                # Save details to state
                st.session_state.photo_bytes = photo.getvalue()
                st.session_state.photo_hash = get_file_hash(photo.getvalue())
                st.session_state.desc = desc
                st.session_state.cost = cost
                st.session_state.phone = client_phone
                st.session_state.step = 2
                st.rerun()

# ---------------------------------------------------------
# 5. STEP 2: CLIENT SIGNATURE (OTP)
# ---------------------------------------------------------
if st.session_state.step == 2:
    st.markdown("### ✍️ Step 2: Client Authorization")
    
    # Review Box
    with st.container():
        st.info(f"**Review Order:** {st.session_state.desc} | **₹{st.session_state.cost}**")
        
    col1, col2 = st.columns(2)
    
    # Send OTP Button
    if not st.session_state.otp_sent:
        st.write("Ask the client to approve this amount.")
        if st.button("📲 Send Aadhaar OTP"):
            with st.spinner("Connecting to UIDAI..."):
                time.sleep(1.5) # Fake delay
                st.session_state.otp_sent = True
                st.rerun()
    
    # Enter OTP Section
    else:
        st.success(f"OTP sent to {st.session_state.phone}")
        otp_input = st.text_input("Enter the 4-digit OTP received", max_chars=4)
        
        if st.button("✅ Verify & Sign", type="primary"):
            if otp_input: # In real app, check if otp_input == real_otp
                with st.spinner("Verifying Biometrics..."):
                    time.sleep(1)
                    st.session_state.signed = True
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.error("Please enter the OTP.")

# ---------------------------------------------------------
# 6. STEP 3: BLOCKCHAIN CERTIFICATE
# ---------------------------------------------------------
if st.session_state.step == 3:
    
    # Anchor to Blockchain (Only once)
    if 'tx_link' not in st.session_state:
        with st.spinner("Minting Immutable Proof on Polygon..."):
            st.session_state.tx_link = anchor_to_polygon(
                st.session_state.photo_hash, 
                st.session_state.desc, 
                st.session_state.cost
            )
    
    st.markdown(f"""
    <div class="success-box">
        <h2>PAYMENT LOCKED 🔒</h2>
        <p>This document is now legally binding.</p>
        <div style="background:#f3f4f6; padding:15px; border-radius:8px; margin-top:15px; text-align:left;">
            <p><b>📅 Date:</b> 10 Dec 2025, 10:42 AM</p>
            <p><b>💰 Amount:</b> ₹{st.session_state.cost}</p>
            <p><b>📝 Work:</b> {st.session_state.desc}</p>
            <p><b>🆔 Digital ID:</b> {st.session_state.photo_hash[:12]}...</p>
        </div>
        <br>
        <a href="{st.session_state.tx_link}" target="_blank" style="
            background-color:#1e293b; 
            color:white; 
            padding:12px 24px; 
            text-decoration:none; 
            border-radius:6px; 
            font-weight:600; 
            display:inline-block;">
            View Proof on Polygon Scan ↗
        </a>
    </div>
    <br>
    <p style="text-align:center; color:#94a3b8; font-size:12px;">
        Legal Note: This digital record is admissible under Section 65B of the Indian Evidence Act.
    </p>
    """, unsafe_allow_html=True)
    
    if st.button("Start New Order"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
