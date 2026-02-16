import os
import json
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class ECIESDecryptor:
    
    def __init__(self, server_private_key_path: str, password: bytes = None):

        if not os.path.exists(server_private_key_path):
            raise FileNotFoundError(f"Private key file not found: {server_private_key_path}")
        
        with open(server_private_key_path, "rb") as f:
                self.server_private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=password
                )

    def decrypt(self, ephemeral_pub_pem: str, encrypted_payload_hex: str) -> dict:
       # Load ephemeral public key
        ephemeral_pub_key = serialization.load_pem_public_key(ephemeral_pub_pem.encode())

        # Convert encrypted payload from hex to bytes
        encrypted_payload = bytes.fromhex(encrypted_payload_hex)

        # Extract nonce, tag, ciphertext
        nonce = encrypted_payload[:12]
        tag = encrypted_payload[12:28]
        ciphertext = encrypted_payload[28:]

        # Derive shared secret using ECDH
        shared_secret = self.server_private_key.exchange(ec.ECDH(), ephemeral_pub_key)

        # Derive AES key from shared secret
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"auction-encryption"
        ).derive(shared_secret)

        # Decrypt using AES-GCM
        decryptor = Cipher(algorithms.AES(derived_key), modes.GCM(nonce, tag)).decryptor()
        plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()

        # Convert to JSON
        return json.loads(plaintext_bytes.decode())
