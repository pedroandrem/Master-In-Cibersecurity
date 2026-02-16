from dataclasses import dataclass
from functools import cached_property
import hashlib

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes



@dataclass(frozen=True)
class KeyPair:
    
    private_key: ec.EllipticCurvePrivateKey

    @classmethod
    def from_identity(cls, mnemonic: str, passphrase: str = "") -> "KeyPair":
        secret = (mnemonic + passphrase).encode()
        salt = hashlib.sha256(secret).digest()

        key_bytes = hash_secret_raw(
            secret=secret,
            salt=salt,
            time_cost=3,
            memory_cost=64 * 1024,
            parallelism=4,
            hash_len=32,
            type=Type.ID,
        )

        order = int(
            "FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551", 
            16
        )

        private_value = int.from_bytes(key_bytes, "big") % order or 1
        private_key = ec.derive_private_key(private_value, ec.SECP256R1())
        return cls(private_key=private_key)


    @cached_property
    def public_pem(self) -> str:
        return self.private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
    

    def sign(self, message:str) -> str:
        sig = self.private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))
        return sig.hex()
