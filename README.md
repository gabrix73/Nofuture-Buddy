# Nofuture-Age
<h2>Installation on Debian</h2>
<p>
  1. Install required packages:<br>
  <code>sudo apt update && sudo apt install apache2 python3 python3-venv</code>
</p>
<p>
  2. Clone this repository and set up your Python environment in the application directory:
  <br>
  <code>git clone https://github.com/gabrix73/Nofuture-Age</code><br>
  <code>cd Nofuture-Age</code><br>
  <code>python3 -m venv nofuture-venv</code><br>
  <code>source nofuture-venv/bin/activate</code><br>
  <code>pip install -r requirements.txt</code> (Assicurati di avere le dipendenze necessarie)<br>
</p>
 requirements.txt: Flask,PyNacl
<br><p>
  3. Place the <code>index.html</code> in the Apache DocumentRoot (e.g., <code>/var/www</code>) and configure your Python backend accordingly.
</p>

<h2>Recommended configuration for apache2 vrtualhost</h2>
<p>
  Ecco un esempio di configurazione per un VirtualHost con supporto TLSv1.3 e RemoteIP:
</p>
<pre>
    SSLProtocol -all +TLSv1.3
    Protocols h2 http/1.1
    # RemoteIP configuration to avoid logging client IPs (NOLOG)
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

    # Buddy system: pair_sessions
    ProxyPass "/pair_sessions" "http://127.0.0.1:7771/pair_sessions"
    ProxyPassReverse "/pair_sessions" "http://127.0.0.1:7771/pair_sessions"

    # Buddy system: buddy_encrypt
    ProxyPass "/buddy_encrypt" "http://127.0.0.1:7771/buddy_encrypt"
    ProxyPassReverse "/buddy_encrypt" "http://127.0.0.1:7771/buddy_encrypt"

    # Buddy system: buddy_decrypt
    ProxyPass "/buddy_decrypt" "http://127.0.0.1:7771/buddy_decrypt"
    ProxyPassReverse "/buddy_decrypt" "http://127.0.0.1:7771/buddy_decrypt"
   
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</pre>

<h2>Decryption Error: InvalidTag</h2>
<p>During the decryption process, users used to encounter the InvalidTag error. 
  This error typically arises when the authentication tag appended to the ciphertext does not match the expected value during verification. 
  Possible causes include:</p>

Data Tampering: The ciphertext may have been altered or corrupted during transmission.
Incorrect Keys: Mismatched or incorrect encryption/decryption keys between paired sessions.
Nonce Reuse: Reusing nonces can compromise the security of the encrypted data, leading to authentication failures.

Resolution Steps:

Ensure Key Consistency: Verify that both parties are using the correct and matching key pairs.
Validate Data Integrity: Implement checks to ensure that the ciphertext remains unaltered during transfer.
Proper Nonce Management: Utilize unique nonces for each encryption operation to maintain security and prevent reuse.

🔧 Technical Functionalities
Our application leverages robust cryptographic practices to ensure secure communication between paired sessions. 
Key features include:

Session Management: Create and manage unique sessions identified by Session IDs, facilitating secure pairing between users.
Buddy System: Pair two sessions to enable mutual encryption and decryption of messages, ensuring that only paired buddies can communicate securely.
Encryption/Decryption: Utilize authenticated encryption to protect message confidentiality and integrity, preventing unauthorized access and tampering.
In-Memory Data Protection: NOT YET IMPLEMENTED MemGuard to safeguard sensitive data in RAM, reducing the risk of memory scraping and data leakage.

🤝 Why Adopt the Buddy System?
The Buddy System enhances security by establishing a trusted connection between two users. Benefits include:

Mutual Authentication: Ensures that both parties verify each other's identities before establishing a communication channel.
Secure Key Exchange: Facilitates the safe exchange of cryptographic keys without exposing them to potential interceptors.
Simplified Pairing: Streamlines the process of connecting users, making secure communication accessible and user-friendly.

🔒 Why Libsodium with PyNaCl?
We chose Libsodium paired with PyNaCl for our cryptographic needs due to their proven security, performance, and ease of integration:

Proven Security: Libsodium is a well-regarded, high-security library trusted by the industry for implementing cryptographic operations.
Ease of Use: PyNaCl provides Python bindings for Libsodium, offering a simple and intuitive API for developers to implement encryption, decryption, and key management.
Performance: Both libraries are optimized for speed and efficiency, ensuring that cryptographic operations do not become a bottleneck in the application.
Comprehensive Features: Support for modern encryption algorithms, authenticated encryption, key exchange mechanisms, and secure memory management aligns with our security requirements.

📚 Additional Resources
MemGuard Documentation: https://github.com/awnumar/memguard
PyNaCl Documentation: https://pynacl.readthedocs.io/en/stable/
Libsodium Documentation: https://libsodium.gitbook.io/doc/
Content Security Policy (CSP) Guide: MDN Web Docs on CSP
</p>
<h2>License</h2>
<p>
  This project is licensed under the <strong>MIT License</strong>.
</p>
