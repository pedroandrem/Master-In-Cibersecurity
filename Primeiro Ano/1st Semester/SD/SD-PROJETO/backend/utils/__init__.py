__version__ = "2025.11.12"

C_END = '\033[0m'
C_GREEN = '\033[92m'
C_RED = '\033[91m'
C_YELLOW = '\033[93m'

try:
    from .ca_client import CertificateAuthorityClient
    from .crypto_utils import KeyPair
    from .identity import UserIdentity
    from .certs_db import get_or_create_cert
    from .jwtValidator import JWTValidator
    from .certValidator import CertValidator
    from .eciesdecryptor import ECIESDecryptor
    print(C_GREEN + f"{__package__}: " + C_YELLOW + f"(version {__version__})" + C_END)
except ImportError as e:
    print(C_RED + f"Error importing baseCommand package: {e}" + C_END)