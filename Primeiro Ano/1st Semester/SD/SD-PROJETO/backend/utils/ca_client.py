from dataclasses import dataclass
import requests

@dataclass
class CertificateAuthorityClient:

    base_url: str = "http://localhost:9000"

    def register(self, public_pem: str) -> str:
        response = requests.post(f"{self.base_url}/api/sign-csr", json={"public_key": public_pem})
        response.raise_for_status()
        return response.json().get("certificate")


    def issue_token(self, cert: str) -> str:
        response = requests.post(f"{self.base_url}/api/issue", json={"cert": cert})
        response.raise_for_status()
        return response.json()["token"]


    def get_timestamp(self) -> tuple[int, str]:
        response = requests.get(f"{self.base_url}/api/timestamp")
        response.raise_for_status()
        data = response.json()
        ts, sig = data.get("timestamp"), data.get("signature")
        if not ts or not sig:
            raise Exception("Invalid timestamp response from CA")
        return ts, sig

