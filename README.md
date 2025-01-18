# Nofuture-Age
<h1>Nofuture-Age Web Interface</h1>
This application is based on <b>FiloSottile/Age</b> present also in the Debian Stable repositories.
My idea is to use it alongside mainstream messaging applications for encrypting/decrypting of text messages.
As long as the session is active you will be able to encrypt text for your interlocutor and decrypt it.
Once the session is ended, the keys used in the previous session are lost making it impossible to retrieve the plaintexts.
The purpose of this approach is not to leave any data after a conversation.
<h2>Installation on Debian</h2>
<p>
  1. Install required packages:<br>
  <code>sudo apt update && sudo apt install age apache2 python3 python3-venv</code>
</p>
<p>
  2. Clone this repository and set up your Python environment in the application directory:
  <br>
  <code>git clone https://github.com/gabrix73/Nofuture-Age</code><br>
  <code>Nofuture-Age</code><br>
  <code>python3 -m venv nofuture-venv</code><br>
  <code>source nofuture-venv/bin/activate</code><br>
  <code>pip install -r requirements.txt</code> (Assicurati di avere le dipendenze necessarie)<br>
</p>
 requirements.txt: Flask>=2.0
<br><p>
  3. Place the <code>index.html</code> in the Apache DocumentRoot (e.g., <code>/var/www</code>) and configure your Python backend accordingly.
</p>

<h2>Recommended configuration for apache2 vrtualhost</h2>
<p>
  Ecco un esempio di configurazione per un VirtualHost con supporto TLSv1.3 e RemoteIP:
</p>
<p><code>
    SSLProtocol -all +TLSv1.3

    Protocols h2 http/1.1

    # RemoteIP configuration to avoid logging client IPs
    # a2enmod remoteip
    RemoteIPHeader X-Forwarded-For
    LogFormat "- - [%{%d/%b/%Y:%H:%M:%S %z}t] \"%r\" %>s %b" noip
    CustomLog /var/log/apache2/safecomms_access.log noip
    #ErrorLog /var/log/apache2/safecomms_error.log

    ProxyRequests Off
    ProxyPreserveHost On
    ProxyPass "/start_session" "http://127.0.0.1:7771/start_session"
    ProxyPassReverse "/start_session" "http://127.0.0.1:7771/start_session"

    ProxyPass "/end_session" "http://127.0.0.1:7771/end_session"
    ProxyPassReverse "/end_session" "http://127.0.0.1:7771/end_session"

    ProxyPass "/encrypt" "http://127.0.0.1:7771/encrypt"
    ProxyPassReverse "/encrypt" "http://127.0.0.1:7771/encrypt"

    ProxyPass "/decrypt" "http://127.0.0.1:7771/decrypt"
    ProxyPassReverse "/decrypt" "http://127.0.0.1:7771/decrypt
</code></p>

<h2>Why Use Age Instead of Ed25519/X25519/AES256-GCM?</h2>
<p>
  We preferred to use <strong>Age</strong> for several reasons:
</p>
<ul>
  <li><strong>Simplicity:</strong> Age provides a straightforward command-line interface for encryption and decryption without the complexities of manual key derivation and management.</li>
  <li><strong>Ease of Integration:</strong> By leveraging the official Age tool, we offload much of the cryptographic heavy lifting to well-maintained, audited code, reducing potential errors like <code>InvalidTag</code> issues.</li>
  <li><strong>Ephemeral Keys:</strong> The application generates temporary keys for each session, and once the session ends, these keys are lost forever, enhancing security.</li>
</ul>
<p></p>Age is designed primarily for encryption and decryption without built-in mechanisms for digital signatures and verification of the sender's identity.<br> 
Here’s why signing and verifying aren’t required within Age’s core design.<br>
<p></p>Along with the cryptographic protocols it uses:</p>
<ul>

<li>X25519:<br>
<p>Age uses the X25519 elliptic-curve Diffie–Hellman key agreement protocol to derive a shared secret between the sender and recipient. This shared secret is used to generate a symmetric key for encryption. X25519 handles key exchange securely but does not inherently provide a digital signature or verification of the sender. It's focused solely on establishing a secret key.</p></li>

<li>ChaCha20-Poly1305 (AEAD):<br>
<p>Once a shared key is derived via X25519, Age employs the ChaCha20 stream cipher for encryption combined with the Poly1305 authenticator. This combination—known as an AEAD (Authenticated Encryption with Associated Data) scheme—ensures that the ciphertext cannot be altered without detection. The Poly1305 tag verifies the integrity and authenticity of the message in the sense that any tampering would be detected, but it does not verify the identity of the sender. It only assures that the message hasn't been modified since encryption.</p></li>
</ul>
<p>Because Age uses an AEAD scheme like ChaCha20-Poly1305, it provides:</p>
<ul>
<li>Confidentiality: The plaintext is kept secret.</li>
<li>Integrity: Any modification of the ciphertext can be detected.</li>
  </ul>
<b>However:</b>
<p>Age does not provide non-repudiation or authentication of the sender's identity through digital signatures. There's no built-in mechanism to cryptographically prove who sent the message.</p>
<p>
  Note that Age focuses on encryption/decryption without built-in signing. This decision was made for simplicity, as incorporating signing (like Ed25519) would add complexity. Our use case prioritizes easy text encryption/decryption alongside mainstream messaging apps.
</p>

<h2>License</h2>
<p>
  This project is licensed under the <strong>MIT License</strong>.
</p>
