import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives import serialization


def generate_key_pair() -> tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]:
    private_key: EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
    public_key: EllipticCurvePublicKey = private_key.public_key()

    cert_dir: str = os.path.join(os.path.dirname(__file__), "certs")
    os.makedirs(cert_dir, exist_ok=True)
    private_path: str = os.path.join(cert_dir, "ca_private.pem")
    public_path: str = os.path.join(cert_dir, "ca_public.pem")

    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("Key pair generated.")
    return private_key, public_key


if __name__ == "__main__":
    priv, pub = generate_key_pair()
