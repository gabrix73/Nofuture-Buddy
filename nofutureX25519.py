#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# nofutureX25519.py
# ------------------------------------------------------------------------------
# Questo esempio mostra come integrare "Age" (l'eseguibile ufficiale) in un'app Flask
# per cifrare/decrittare testi. Non c'è firma, solo cifratura.
#
# Flow:
#   1) /start_session  -> genera ephemeral private key (con age-keygen), memorizza in RAM
#   2) /end_session    -> elimina la private key dalla RAM
#   3) /encrypt        -> usa "age -r <pubKeyRecipient>" per cifrare (via subprocess)
#   4) /decrypt        -> usa "age -d -i <privateKey>" per decrittare
#
# Tutto è gestito in memoria: si usano file temporanei per interagire con i binari Age.
# ------------------------------------------------------------------------------
import os
import base64
import json
import subprocess
import tempfile
import traceback

from flask import Flask, request, jsonify

app = Flask(__name__)

# In memoria:
# SESSIONS[session_id] = {
#   'private_key_str': <str>,
#   'public_key_str':  <str>
# }
SESSIONS = {}

# ------------------------------------------------------------------------------
# Funzioni di supporto a "age"
# ------------------------------------------------------------------------------

def generate_age_keypair():
    """
    Esegue 'age-keygen' e cerca di estrarre la linea della chiave pubblica.
    Ritorna (private_key_text, public_key_str).
    """
    proc = subprocess.run(
        ["age-keygen"],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"age-keygen failed: {proc.stderr}")

    full_key = proc.stdout
    pubKeyLine = None
    for line in full_key.splitlines():
        if line.startswith("# public key:"):
            pubKeyLine = line.strip()
            break
    if not pubKeyLine:
        raise ValueError("Cannot find public key line in age-keygen output.")

    parts = pubKeyLine.split("public key:")
    if len(parts) < 2:
        raise ValueError("Malformed public key line.")
    public_key = parts[1].strip()

    return full_key, public_key

def age_encrypt(recipient_pub_key, plaintext):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpIn:
        tmpIn.write(plaintext)
        tmpIn.flush()
        inName = tmpIn.name

    outName = inName + ".age"

    try:
        proc = subprocess.run(
            ["age", "-r", recipient_pub_key, "-o", outName, inName],
            capture_output=True,
            text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"age encrypt failed: {proc.stderr}")

        with open(outName, "rb") as f:
            cipher_bytes = f.read()
        encrypted_b64 = base64.b64encode(cipher_bytes).decode('utf-8')
        return encrypted_b64
    finally:
        try: os.remove(inName)
        except: pass
        try: os.remove(outName)
        except: pass

def age_decrypt(private_key_text, ciphertext_b64):
    raw_cipher = base64.b64decode(ciphertext_b64)
    with tempfile.NamedTemporaryFile(delete=False) as tmpCipher:
        tmpCipher.write(raw_cipher)
        tmpCipher.flush()
        cipherName = tmpCipher.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpKey:
        tmpKey.write(private_key_text)
        tmpKey.flush()
        privName = tmpKey.name

    outName = cipherName + ".dec"

    try:
        proc = subprocess.run(
            ["age", "-d", "-i", privName, "-o", outName, cipherName],
            capture_output=True,
            text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"age decrypt failed: {proc.stderr}")

        with open(outName, "r", encoding="utf-8") as f:
            plaintext = f.read()
        return plaintext
    finally:
        for fname in [cipherName, privName, outName]:
            try: os.remove(fname)
            except: pass

# ------------------------------------------------------------------------------
# ROUTE Flask
# ------------------------------------------------------------------------------

@app.route('/start_session', methods=['POST'])
def start_session():
    try:
        privateKeyStr, publicKeyStr = generate_age_keypair()
        session_id = base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8').rstrip('=')

        SESSIONS[session_id] = {
            'private_key_str': privateKeyStr,
            'public_key_str':  publicKeyStr
        }

        return jsonify({
            "session_id": session_id,
            "public_key": publicKeyStr
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"{e.__class__.__name__}: {str(e)}"}), 400

@app.route('/end_session', methods=['POST'])
def end_session():
    data = request.get_json(force=True)
    sid = data.get('session_id')
    if sid and sid in SESSIONS:
        del SESSIONS[sid]
        return jsonify({"status": "ended", "session_id": sid})
    else:
        return jsonify({"error": "Invalid session_id"}), 400

@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    data = request.get_json(force=True)
    sid = data.get('session_id')
    recipient_pub = data.get('recipient_public_key_b64')
    plaintext = data.get('plaintext')

    if not sid or sid not in SESSIONS:
        return jsonify({"error": "Invalid or missing session_id"}), 400
    if not recipient_pub or not plaintext:
        return jsonify({"error": "Missing recipient_public_key_b64 or plaintext"}), 400

    try:
        encrypted_b64 = age_encrypt(recipient_pub, plaintext)
        return jsonify({"encrypted_b64": encrypted_b64})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"{e.__class__.__name__}: {str(e)}"}), 400

@app.route('/decrypt', methods=['POST'])
def decrypt_endpoint():
    data = request.get_json(force=True)
    sid = data.get('session_id')
    enc = data.get('encrypted_b64')

    if not sid or sid not in SESSIONS:
        return jsonify({"error": "Invalid or missing session_id"}), 400
    if not enc:
        return jsonify({"error": "Missing encrypted_b64"}), 400

    try:
        privateKeyStr = SESSIONS[sid]['private_key_str']
        plaintext = age_decrypt(privateKeyStr, enc)
        return jsonify({"plaintext": plaintext})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"{e.__class__.__name__}: {str(e)}"}), 400

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=7771, debug=False)
