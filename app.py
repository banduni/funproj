import streamlit as st
from chain_utils import get_file_hash, anchor_to_polygon
from aadhaar_utils import create_signing_request_MOCK
import time

# ---------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="SiteSign | Enterprise",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

# ---------------------------------------------------------
# 2. PROFESSIONAL CSS (The "SaaS" Look)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* REMOVE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* MAIN BACKGROUND */
    .stApp {
        background-color: #f8fafc; /* Very Light Blue-Gray */
    }

    /* CARD DESIGN */
    .css-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }

    /* INPUT FIELDS */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        padding: 10px;
        font-size: 16px;
        color: #0f172a;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #334155 !important;
        font-weight: 600;
    }

    /* BUTTONS */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1rem;
        font-size: 16px;
        border: none;
        transition: all 0.2s;
    }
    
    /* Primary Button */
    div.stButton > button:first-child {
        background-color: #2563eb; /* Blue */
        color: white;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
    }

    /* PROGRESS STEPS */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        padding: 0 10px;
    }
    .step-active {
        color: #2563eb;
    }
    
    /* CERTIFICATE STYLE */
    .certificate {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 2px solid #22c55e;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }
    .badge {
        background: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. APP HEADER
# ---------------------------------------------------------

# Simple Logo Area
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #0f172a; margin:0; font-weight: 800;">🛡️ SiteSign</h2>
    <p style="color: #64748b; font-size: 14px; margin-top: 5px;">Enterprise Grade Payment Protection</p>
</div>
""", unsafe_allow_html=True)

# Visual Step Indicator
step_html = f"""
<div class="step-indicator">
    <span class="{'step-active' if st.session_state.step >= 1 else ''}">1. EVIDENCE</span>
    <span class="{'step-active' if st.session_state.step >= 2 else ''}">2. APPROVAL</span>
    <span class="{'step-active' if st.session_state.step >= 3 else ''}">3. LOCKED</span>
</div>
<div style="height: 4px; background: #e2e8f0; border-radius: 2px; margin-bottom: 20px; overflow: hidden;">
    <div style="height: 100%; width: {st.session_state.step * 33}%; background: #2563eb; transition: width 0.5s;"></div>
</div>
"""
st.markdown(step_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. STEP 1: CAPTURE EVIDENCE (Form Logic)
# ---------------------------------------------------------
if st.session_state.step == 1:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("#### 📸 New Change Order")
    
    # FORM START
    with st.form("entry_form", clear_on_submit=False):
        photo = st.camera_input("Site Photo")
        st.write("") 
        
        desc = st.text_area("Scope Description", height=80, placeholder="e.g. Client requested Italian Marble...")
        
        c1, c2 = st.columns(2)
        with c1:
            cost = st.number_input("Extra Cost (₹)", min_value=0, step=1000)
        with c2:
            client_phone = st.text_input("Client Mobile", placeholder="98765...")
        
        st.write("")
        
        # Form Submit Button
        submitted = st.form_submit_button("Proceed to Sign ➡️")
        
        if submitted:
            if photo and desc and cost > 0 and client_phone:
                st.session_state.photo_bytes = photo.getvalue()
                st.session_state.photo_hash = get_file_hash(photo.getvalue())
                st.session_state.desc = desc
                st.session_state.cost = cost
                st.session_state.phone = client_phone
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please fill all details.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trust Signals
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 20px;">
        🔒 Encrypted • 🇮🇳 Govt. Admissible • ⚡ Instant
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. STEP 2: AUTHORIZATION
# ---------------------------------------------------------
elif st.session_state.step == 2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    # Summary Ticket
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="color: #64748b; font-size: 12px;">ITEM</span>
            <span style="color: #0f172a; font-weight: 600; font-size: 12px;">CHANGE ORDER #001</span>
        </div>
        <div style="color: #334155; font-weight: 500; margin-bottom: 10px;">{st.session_state.desc}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 10px;">
            <span style="color: #64748b;">Total Amount</span>
            <span style="color: #2563eb; font-weight: 700; font-size: 18px;">₹{st.session_state.cost:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.otp_sent:
        st.write("**Authorize Payment**")
        st.write("Send a secure Aadhaar link to the client.")
        
        if st.button("📱 Send OTP via Digio"):
            with st.spinner("Connecting to UIDAI Server..."):
                time.sleep(1.5)
                st.session_state.otp_sent = True
                st.rerun()
        
        if st.button("⬅️ Edit Details"):
            st.session_state.step = 1
            st.rerun()

    else:
        st.success(f"OTP Sent to {st.session_state.phone}")
        
        # OTP Entry Form
        with st.form("otp_form"):
            otp = st.text_input("Enter 4-Digit OTP", max_chars=4, placeholder="XXXX")
            verify_btn = st.form_submit_button("✅ Verify & Lock Contract")
            
            if verify_btn:
                if otp:
                    with st.spinner("Verifying Biometrics & Minting to Polygon..."):
                        time.sleep(2)
                        st.session_state.step = 3
                        st.rerun()
                else:
                    st.warning("Enter OTP to proceed.")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. STEP 3: SUCCESS CERTIFICATE
# ---------------------------------------------------------
elif st.session_state.step == 3:
    
    if 'tx_link' not in st.session_state:
        st.session_state.tx_link = anchor_to_polygon(
            st.session_state.photo_hash, 
            st.session_state.desc, 
            st.session_state.cost
        )

    # We define the HTML first to ensure it processes as a string
    certificate_html = f"""
    <div class="certificate">
        <div class="badge">✓ LEGALLY BINDING</div>
        <h2 style="color: #15803d; margin-top: 5px;">Payment Secured</h2>
        <p style="color: #374151; font-size: 14px;">This agreement has been permanently anchored to the Polygon Blockchain.</p>
        
        <div style="margin: 20px 0; text-align: left; background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>👤 Signer:</b> Verified Aadhaar User</p>
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>💰 Value:</b> ₹{st.session_state.cost:,}</p>
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>🕒 Time:</b> {time.strftime("%d %b %Y, %I:%M %p")}</p>
            <p style="margin: 5px 0; font-size: 10px; color: #94a3b8;">HASH: {st.session_state.photo_hash[:16]}...</p>
        </div>

        <a href="{st.session_state.tx_link}" target="_blank" style="text-decoration: none;">
            <button style="
                background: #0f172a; 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                font-weight: 600; 
                cursor: pointer; 
                width: 100%;">
                View Blockchain Proof ↗
            </button>
        </a>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <p style="font-size: 11px; color: #64748b;">
            Admissible under <b>Section 65B, Indian Evidence Act 1872</b>.
        </p>
    </div>
    """
    
    # RENDER THE HTML
    st.markdown(certificate_html, unsafe_allow_html=True)
    
    if st.button("Start New Project"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()    header {visibility: hidden;}

    /* MAIN BACKGROUND */
    .stApp {
        background-color: #f1f5f9; /* Light Blue-Gray */
    }

    /* CARD DESIGN */
    .css-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }

    /* INPUT FIELDS */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 10px;
        font-size: 16px;
        color: #0f172a; /* Dark Text */
    }
    .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #334155 !important;
        font-weight: 600;
    }

    /* BUTTONS */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1rem;
        font-size: 16px;
        border: none;
        transition: all 0.2s;
    }
    
    /* Primary Button */
    div.stButton > button:first-child {
        background-color: #2563eb;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
    }

    /* PROGRESS STEPS */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        padding: 0 10px;
    }
    .step-active {
        color: #2563eb;
    }
    
    /* CERTIFICATE STYLE */
    .certificate {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 2px solid #22c55e;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }
    .badge {
        background: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. APP HEADER
# ---------------------------------------------------------

# Simple Logo Area
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #0f172a; margin:0; font-weight: 800;">🛡️ SiteSign</h2>
    <p style="color: #64748b; font-size: 14px; margin-top: 5px;">Enterprise Grade Payment Protection</p>
</div>
""", unsafe_allow_html=True)

# Visual Step Indicator
step_html = f"""
<div class="step-indicator">
    <span class="{'step-active' if st.session_state.step >= 1 else ''}">1. EVIDENCE</span>
    <span class="{'step-active' if st.session_state.step >= 2 else ''}">2. APPROVAL</span>
    <span class="{'step-active' if st.session_state.step >= 3 else ''}">3. LOCKED</span>
</div>
<div style="height: 4px; background: #e2e8f0; border-radius: 2px; margin-bottom: 20px; overflow: hidden;">
    <div style="height: 100%; width: {st.session_state.step * 33}%; background: #2563eb; transition: width 0.5s;"></div>
</div>
"""
st.markdown(step_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. STEP 1: CAPTURE EVIDENCE (With Form)
# ---------------------------------------------------------
if st.session_state.step == 1:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("#### 📸 New Change Order")
    st.markdown("<p style='color:#64748b; font-size:14px;'>Capture site conditions to lock in extra payment.</p>", unsafe_allow_html=True)
    
    # FORM START
    with st.form("entry_form", clear_on_submit=False):
        photo = st.camera_input("Site Photo")
        st.write("") 
        
        desc = st.text_area("Scope Description", height=80, placeholder="e.g. Client requested Italian Marble...")
        
        c1, c2 = st.columns(2)
        with c1:
            cost = st.number_input("Extra Cost (₹)", min_value=0, step=1000)
        with c2:
            client_phone = st.text_input("Client Mobile", placeholder="98765...")
        
        st.write("")
        
        # Form Submit Button
        submitted = st.form_submit_button("Proceed to Sign ➡️")
        
        if submitted:
            if photo and desc and cost > 0 and client_phone:
                st.session_state.photo_bytes = photo.getvalue()
                st.session_state.photo_hash = get_file_hash(photo.getvalue())
                st.session_state.desc = desc
                st.session_state.cost = cost
                st.session_state.phone = client_phone
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please fill all details.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trust Signals
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 20px;">
        🔒 Encrypted • 🇮🇳 Govt. Admissible • ⚡ Instant
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. STEP 2: AUTHORIZATION
# ---------------------------------------------------------
elif st.session_state.step == 2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    # Summary Ticket
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="color: #64748b; font-size: 12px;">ITEM</span>
            <span style="color: #0f172a; font-weight: 600; font-size: 12px;">CHANGE ORDER #001</span>
        </div>
        <div style="color: #334155; font-weight: 500; margin-bottom: 10px;">{st.session_state.desc}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 10px;">
            <span style="color: #64748b;">Total Amount</span>
            <span style="color: #2563eb; font-weight: 700; font-size: 18px;">₹{st.session_state.cost:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.otp_sent:
        st.write("**Authorize Payment**")
        st.write("Send a secure Aadhaar link to the client.")
        
        # Using a form here isn't strictly necessary but keeps UI consistent
        if st.button("📱 Send OTP via Digio"):
            with st.spinner("Connecting to UIDAI Server..."):
                time.sleep(1.5)
                st.session_state.otp_sent = True
                st.rerun()
        
        if st.button("⬅️ Edit Details"):
            st.session_state.step = 1
            st.rerun()

    else:
        st.success(f"OTP Sent to {st.session_state.phone}")
        
        # OTP Entry Form
        with st.form("otp_form"):
            otp = st.text_input("Enter 4-Digit OTP", max_chars=4, placeholder="XXXX")
            verify_btn = st.form_submit_button("✅ Verify & Lock Contract")
            
            if verify_btn:
                if otp:
                    with st.spinner("Verifying Biometrics & Minting to Polygon..."):
                        time.sleep(2)
                        st.session_state.step = 3
                        st.rerun()
                else:
                    st.warning("Enter OTP to proceed.")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. STEP 3: SUCCESS CERTIFICATE
# ---------------------------------------------------------
elif st.session_state.step == 3:
    
    if 'tx_link' not in st.session_state:
        st.session_state.tx_link = anchor_to_polygon(
            st.session_state.photo_hash, 
            st.session_state.desc, 
            st.session_state.cost
        )

    # Certificate UI
    st.markdown(f"""
    <div class="certificate">
        <div class="badge">✓ LEGALLY BINDING</div>
        <h2 style="color: #15803d; margin-top: 5px;">Payment Secured</h2>
        <p style="color: #374151; font-size: 14px;">This agreement has been permanently anchored to the Polygon Blockchain.</p>
        
        <div style="margin: 20px 0; text-align: left; background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>👤 Signer:</b> Verified Aadhaar User</p>
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>💰 Value:</b> ₹{st.session_state.cost:,}</p>
            <p style="margin: 5px 0; font-size: 14px; color:#334155;"><b>🕒 Time:</b> {time.strftime("%d %b %Y, %I:%M %p")}</p>
            <p style="margin: 5px 0; font-size: 10px; color: #94a3b8;">HASH: {st.session_state.photo_hash[:16]}...</p>
        </div>

        <a href="{st.session_state.tx_link}" target="_blank" style="text-decoration: none;">
            <button style="
                background: #0f172a; 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                font-weight: 600; 
                cursor: pointer; 
                width: 100%;">
                View Blockchain Proof ↗
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p style="font-size: 11px; color: #64748b;">
            Admissible under <b>Section 65B, Indian Evidence Act 1872</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Start New Project"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


