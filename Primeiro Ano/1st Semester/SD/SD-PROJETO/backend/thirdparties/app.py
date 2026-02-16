from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from jwtClaims import JWTClaims
import datetime
from typing import Any
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


app = Flask(__name__)
CORS(app, origins="*")


simulated_time: datetime.date | None = None

with open("./certs/ca_private.pem", "rb") as f:
    ca_private_key: EllipticCurvePrivateKey  = serialization.load_pem_private_key(f.read(), password=None)


with open("./certs/ca_public.pem", "rb") as f:
    ca_public_key: bytes = f.read()


def public_key_fingerprint(pub_key_pem: str) -> str:
    if not isinstance(pub_key_pem, str):
        raise TypeError("Public key must be a string")
    
    pub_key = serialization.load_pem_public_key(pub_key_pem.encode())
    pub_bytes: bytes = pub_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(pub_bytes)
    return digest.finalize().hex()


@app.route("/.well-known/ca-public", methods=["GET"])
def ca_public_endpoint() -> tuple[dict[str, Any], int]:
    payload: dict[str, Any] = {
        "kid": "ca-key-1",                 
        "alg": "ES256",                     
        "public_key": ca_public_key.decode()
    }
    return jsonify(payload), 200


@app.route("/api/sign-csr", methods=["POST"])
def sign_csr() -> tuple[dict[str, str], int]:
    data: dict[str, Any] = request.get_json(silent=True)
    if not data or "public_key" not in data:
        return jsonify({"error": "Missing public_key"}), 400

    public_key_pem: str = data["public_key"]

    if not isinstance(public_key_pem, str):
        return jsonify({"error": "Invalid public_key type"}), 400
    
    try: 
        peer_public_key = serialization.load_pem_public_key(public_key_pem.encode())
    except ValueError:
        return jsonify({"error": "Invalid PEM public key"}), 400

    try:

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u'PT'),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'Braga'),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u'Braga'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'P2P Auction'),
            x509.NameAttribute(NameOID.COMMON_NAME, u'gruposete.mcs.uminho.pt'),
        ])

        now: datetime.datetime = datetime.datetime.now(datetime.UTC)

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(x509.Name([
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyLocalAuctionCA"),
            ]))
            .public_key(peer_public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(private_key=ca_private_key, algorithm=hashes.SHA256())
        )

        cert_pem: str= cert.public_bytes(serialization.Encoding.PEM).decode()
        return jsonify({"certificate": cert_pem}), 200

    except Exception as e:
        app.logger.exception("Failed to sign certificate")
        return jsonify({"error": f"Failed to sign certificate: {str(e)}"}), 500


@app.route("/api/issue", methods=["POST"])
def issue_token() -> tuple[dict[str, str], int]:
    data: dict[str, Any] = request.get_json(silent=True)

    if not data or "cert" not in data:
        return jsonify({"error": "Missing certificate"}), 400
    
    cert_pem: str = data["cert"]

    if not isinstance(cert_pem, str):
        return jsonify({"error": "Invalid certificate type"}), 400
    
    try:
    # Load PEM certificate string into x509 object
        cert_obj = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'))

        # Extract public key object
        peer_public_key = cert_obj.public_key()

        # Optional: convert to PEM string if you need it as text
        peer_public_key_pem = peer_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')  # decode bytes -> str

        # Now you can safely use it for fingerprinting or other operations
        sub: str = public_key_fingerprint(peer_public_key_pem)

    except Exception as e:
        return jsonify({"error": f"Invalid certificate: {str(e)}"}), 400


    claims: JWTClaims = JWTClaims(subject=sub)
    payload: dict[str, Any] = claims.to_payload(issuer="MyLocalAuctionCA")

    token: str = jwt.encode(
        payload,
        ca_private_key,
        algorithm="ES256",
        headers={"kid": "ca-key-1"}
    )

    print("4")

    return jsonify({"token": token}), 200


@app.route("/api/timestamp", methods=["GET"])
def timestamp() -> tuple[dict[str, str], int]:

    real_now = datetime.datetime.now(datetime.timezone.utc)

    if simulated_time:
        ts = datetime.datetime(
            year=simulated_time.year,
            month=simulated_time.month,
            day=simulated_time.day,
            hour=real_now.hour,
            minute=real_now.minute,
            second=real_now.second,
            microsecond=real_now.microsecond,
            tzinfo=real_now.tzinfo
        )
    else:
        ts = real_now

    signature: bytes = ca_private_key.sign(
        ts.isoformat().encode(),
        ec.ECDSA(hashes.SHA256())
    )

    return jsonify({"timestamp": ts.isoformat(), "signature": signature.hex()}), 200


@app.route("/api/settime", methods=["POST"])
def set_time():
    global simulated_time
    data = request.get_json(silent=True)

    if not data or "datetime" not in data:
        return jsonify({"error": "Missing datetime"}), 400

    try:
        date_str = data["datetime"]
        dt = datetime.datetime.fromisoformat(date_str)

        simulated_time = dt.date()

        return jsonify({"message": f"Time is now set to {simulated_time.isoformat()}"}), 200
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400


@app.route("/api/resettime", methods=["POST"])
def reset_time():
    global simulated_time
    simulated_time = None
    return jsonify({"message": "Time simulation reset"}), 200


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=9000)
