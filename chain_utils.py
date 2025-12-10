import os
import hashlib
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

def get_file_hash(bytes_data):
    """Creates a SHA-256 Fingerprint of any file/text"""
    return hashlib.sha256(bytes_data).hexdigest()

def anchor_to_polygon(doc_hash, description, cost):
    """Writes the hash to the Polygon Blockchain"""
    
    # 1. Setup Connection
    rpc_url = os.getenv("RPC_URL")
    private_key = os.getenv("PRIVATE_KEY")
    wallet_addr = os.getenv("WALLET_ADDRESS")
    
    if not private_key or "YOUR" in private_key:
        # Mock Mode (If you haven't set up wallet yet)
        return f"https://amoy.polygonscan.com/tx/0xMOCK_TRANSACTION_HASH_{doc_hash[:10]}"

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        return "Error: Could not connect to Polygon"

    # 2. Create a specific data string to store (The "Memo")
    # Format: "SiteSign: <Hash> | Cost: <Cost>"
    # In a real app, you'd call a Smart Contract. Here, we send a 0 MATIC tx with data.
    data_to_store = f"SiteSign:{doc_hash}|Amt:{cost}|Desc:{description}"
    hex_data = w3.to_hex(text=data_to_store)

    # 3. Build Transaction
    nonce = w3.eth.get_transaction_count(wallet_addr)
    tx = {
        'nonce': nonce,
        'to': wallet_addr, # Sending to yourself just to store data on chain
        'value': 0,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'data': hex_data
    }

    # 4. Sign & Send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    return f"https://amoy.polygonscan.com/tx/{w3.to_hex(tx_hash)}"