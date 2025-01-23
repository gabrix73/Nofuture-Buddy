#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# nofutureX25519_pynacl.py
# ------------------------------------------------------------------------------
# A Flask web application that:
#   - Stores ephemeral X25519 keys in RAM only (no disk).
#   - /start_session      -> Generate a new ephemeral session
#   - /end_session        -> Wipe the session from RAM
#   - /pair_sessions      -> "Buddy system": link two sessions so each knows the other's pubkey
#   - /buddy_encrypt      -> Encrypt from your session to your buddy
#   - /buddy_decrypt      -> Decrypt from your buddy to you
#
# Uses X25519 for ECDH, and PyNaCl's Box for encryption (which uses XSalsa20 and Poly1305).
# Listens on 127.0.0.1:7771 by default.
# ------------------------------------------------------------------------------

import os
import base64
import json
import secrets
import traceback
import hashlib
import logging

from flask import Flask, request, jsonify
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

app = Flask(__name__)

# Configura logging
logging.basicConfig(level=logging.DEBUG)

# In-memory sessions: ephemeral
# SESSIONS[session_id] = {
#   'private_key': <PrivateKey>,
#   'public_key':  <PublicKey>,
#   'buddy_public_key': <PublicKey> or None
# }
SESSIONS = {}

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def generate_x25519_keypair():
    """Generate an X25519 keypair."""
    priv = PrivateKey.generate()
    pub = priv.public_key
    return priv, pub

def encrypt_message(box, plaintext):
    """
    Encrypts the plaintext using the provided Box.
    Returns a base64-encoded JSON string containing ciphertext and nonce.
    """
    ciphertext = box.encrypt(plaintext.encode('utf-8'))
    # PyNaCl's Box.encrypt includes the nonce and ciphertext together
    # To make it JSON-friendly, we'll separate them
    encrypted_data = {
        "ciphertext": base64.b64encode(ciphertext.ciphertext).decode('utf-8'),
        "nonce": base64.b64encode(ciphertext.nonce).decode('utf-8')
    }
    return base64.b64encode(json.dumps(encrypted_data).encode('utf-8')).decode('utf-8')

def decrypt_message(box, encrypted_b64):
    """
    Decrypts the base64-encoded JSON string containing ciphertext and nonce using the provided Box.
    Returns the plaintext string.
    """
    try:
        encrypted_json = base64.b64decode(encrypted_b64).decode('utf-8')
        encrypted_data = json.loads(encrypted_json)
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        plaintext = box.decrypt(ciphertext, nonce)
        return plaintext.decode('utf-8')
    except Exception as e:
        raise ValueError("InvalidTag or decryption failed") from e

# ------------------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------------------

@app.route("/start_session", methods=["POST"])
def start_session():
    """
    Creates a new ephemeral X25519 keypair, returns {session_id, public_key, fingerprint}
    All stored in memory (SESSIONS).
    """
    priv, pub = generate_x25519_keypair()
    pub_raw = pub.encode(encoder=Base64Encoder).decode('utf-8')

    # Generate a unique session_id
    session_id = base64.urlsafe_b64encode(secrets.token_bytes(12)).decode('utf-8').rstrip("=")

    # Save in memory
    SESSIONS[session_id] = {
        "private_key": priv,
        "public_key": pub,
        "buddy_public_key": None
    }

    # Fingerprint for debugging
    fingerprint = hashlib.sha256(base64.b64decode(pub_raw)).digest()
    fingerprint_b64 = base64.b64encode(fingerprint).decode('utf-8')

    return jsonify({
        "session_id": session_id,
        "public_key": pub_raw,
        "fingerprint": fingerprint_b64
    })

@app.route("/end_session", methods=["POST"])
def end_session():
    """
    Expects { "session_id": "..." }
    Removes that session from SESSIONS.
    """
    data = request.get_json(force=True)
    sid = data.get("session_id")
    if sid and sid in SESSIONS:
        del SESSIONS[sid]
        return jsonify({"status":"ended","session_id":sid})
    return jsonify({"error":"Invalid session_id"}), 400

@app.route("/pair_sessions", methods=["POST"])
def pair_sessions():
    """
    Expects { "session_id_A":"...", "session_id_B":"..." }
    Links them. So SESSIONS[sidA]["buddy_public_key"] = pubB, and vice versa.
    Returns { "status":"paired", "session_id_A":..., "public_key_A":..., "session_id_B":..., "public_key_B":... }
    """
    data = request.get_json(force=True)
    sidA = data.get("session_id_A")
    sidB = data.get("session_id_B")

    if not sidA or not sidB:
        return jsonify({"error":"Missing session_id_A or session_id_B"}), 400
    if sidA not in SESSIONS or sidB not in SESSIONS:
        return jsonify({"error":"One or both session IDs invalid"}), 400

    # Retrieve public keys
    pubA = SESSIONS[sidA]["public_key"]
    pubB = SESSIONS[sidB]["public_key"]

    # Link buddies
    SESSIONS[sidA]["buddy_public_key"] = pubB
    SESSIONS[sidB]["buddy_public_key"] = pubA

    return jsonify({
        "status":"paired",
        "session_id_A": sidA,
        "public_key_A": SESSIONS[sidA]["public_key"].encode(encoder=Base64Encoder).decode('utf-8'),
        "session_id_B": sidB,
        "public_key_B": SESSIONS[sidB]["public_key"].encode(encoder=Base64Encoder).decode('utf-8')
    })

@app.route("/buddy_encrypt", methods=["POST"])
def buddy_encrypt():
    """
    Expects { "session_id":"...", "plaintext":"..." }
    Looks up session, finds the buddy, uses buddy's public key for encryption.
    Returns { "encrypted_b64":"..." }
    """
    data = request.get_json(force=True)
    sid = data.get("session_id")
    plaintext = data.get("plaintext")

    logging.debug(f"Encrypt request for session_id: {sid}, plaintext: {plaintext}")

    if not sid or sid not in SESSIONS:
        logging.error("Invalid or missing session_id")
        return jsonify({"error":"Invalid or missing session_id"}), 400
    if not plaintext:
        logging.error("Missing plaintext")
        return jsonify({"error":"Missing plaintext"}), 400

    buddy_pub = SESSIONS[sid].get("buddy_public_key")
    if not buddy_pub:
        logging.error("Session not paired or buddy not found")
        return jsonify({"error":"Session not paired or buddy not found"}), 400

    try:
        # Create Box with own private key and buddy's public key
        box = Box(SESSIONS[sid]["private_key"], buddy_pub)

        # Encrypt the message
        encrypted_b64 = encrypt_message(box, plaintext)
        logging.debug(f"Encrypted message: {encrypted_b64}")
        return jsonify({"encrypted_b64": encrypted_b64})
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        traceback.print_exc()
        return jsonify({"error": f"{e.__class__.__name__}: {str(e)}"}), 400

@app.route("/buddy_decrypt", methods=["POST"])
def buddy_decrypt():
    """
    Expects { "session_id":"...", "encrypted_b64":"..." }
    Uses the buddy's public key to decrypt.
    Returns { "plaintext":"..." }
    """
    data = request.get_json(force=True)
    sid = data.get("session_id")
    encrypted_b64 = data.get("encrypted_b64")

    logging.debug(f"Decrypt request for session_id: {sid}, encrypted_b64: {encrypted_b64}")

    if not sid or sid not in SESSIONS:
        logging.error("Invalid or missing session_id")
        return jsonify({"error":"Invalid or missing session_id"}), 400
    if not encrypted_b64:
        logging.error("Missing encrypted_b64")
        return jsonify({"error":"Missing encrypted_b64"}), 400

    buddy_pub = SESSIONS[sid].get("buddy_public_key")
    if not buddy_pub:
        logging.error("Session not paired or buddy not found")
        return jsonify({"error":"Session not paired or buddy not found"}), 400

    try:
        # Create Box with own private key and buddy's public key
        box = Box(SESSIONS[sid]["private_key"], buddy_pub)

        # Decrypt the message
        plaintext = decrypt_message(box, encrypted_b64)
        logging.debug(f"Decrypted plaintext: {plaintext}")
        return jsonify({"plaintext": plaintext})
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        traceback.print_exc()
        return jsonify({"error": f"{e.__class__.__name__}: {str(e)}"}), 400

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    print(app.url_map)  # <--- debug
    app.run(host="127.0.0.1", port=7771, debug=True)
