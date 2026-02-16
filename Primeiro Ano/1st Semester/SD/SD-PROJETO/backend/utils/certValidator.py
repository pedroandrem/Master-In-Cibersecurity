from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

class CertValidator:
   
    def __init__(self, ca_public_key):
        if not isinstance(ca_public_key, (str, bytes)):
            raise TypeError("CA public key must be a PEM string or bytes")
        if isinstance(ca_public_key, str):
            ca_public_key = ca_public_key.encode()
        self.ca_public_key = serialization.load_pem_public_key(ca_public_key)

    def validate(self, cert_pem, expected_identity):
        if not isinstance(cert_pem, str):
            raise TypeError("Certificate must be a PEM-encoded string")
        if not isinstance(expected_identity, str):
            raise TypeError("Expected idendity must be a string")
        if not cert_pem:
            raise ValueError("Certificate missing")

        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
            if not isinstance(cert, x509.Certificate):
                raise TypeError("Loaded object is not a valid x.509 certificate")
            
            self.ca_public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                ec.ECDSA(hashes.SHA256())
            )

            cn_attrs  = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            if not cn_attrs:
                raise ValueError("Certificate does not contain a Commom Name (CN)")
            cert_cn = cn_attrs[0].value
            if cert_cn != expected_identity:
                raise ValueError(f"Identity mismatch: expected {expected_identity}, got {cert_cn}")

            return cert

        except InvalidSignature as e:
            raise InvalidSignature("Certificate signature invalid") from e
        except Exception as e:
            raise ValueError(f"Certificate verification failed: {str(e)}") from e
