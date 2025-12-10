import time

def create_signing_request_MOCK(file_name, user_phone):
    """
    SIMULATES sending a request to Digio.
    Use this to demo the app to clients immediately.
    """
    time.sleep(1.5) # Fake network delay
    return {
        "status": "success",
        "message": f"SMS sent to {user_phone}. Waiting for Aadhaar OTP...",
        "signing_url": "https://ext.digio.in/mock_signing_page" 
    }

def check_signing_status_MOCK():
    """Simulates the client signing the document"""
    time.sleep(2)
    return True # Always returns "Signed" for demo