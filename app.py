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

# Custom CSS for Professional Look
st.markdown("""
<style>
    /* Clean Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Header Card */
    .header-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Success Certificate */
    .success-box {
        background: #ffffff;
        border: 1px solid #d1fae5;
        border-top: 4px solid #10b981;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.1);
    }
    
    /* Buttons */
    div.stButton > button {
        width: 100%;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#1e293b;">🛡️ SiteSign Pro</h2>
    <p style="margin:5px; color:#64748b; font-size:14px;">Legal Payment Protection for Contractors</p>
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
# 3. STEP 1: CAPTURE
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
# 4. STEP 2: CLIENT SIGNATURE (OTP)
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
# 5. STEP 3: BLOCKCHAIN CERTIFICATE
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
        <h2 style="color:#10b981; margin-top:0;">PAYMENT LOCKED 🔒</h2>
        <p style="color:#374151;">This document is now legally binding.</p>
        <div style="background:#f3f4f6; padding:15px; border-radius:8px; margin-top:15px; text-align:left; font-size:14px;">
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