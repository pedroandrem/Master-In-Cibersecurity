from dataclasses import dataclass, field
import datetime
import uuid
from typing import Any

@dataclass
class JWTClaims:

    subject: str = field(default=None)
    issued_at: datetime.datetime = field(init=False)
    not_before: datetime.datetime = field(init=False)
    expiration: datetime.datetime = field(init=False)
    jwt_id: str = field(init=False)

    def __post_init__(
        self
    ) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        self.issued_at = now
        self.not_before = now
        self.expiration = now + datetime.timedelta(hours=1)
        self.jwt_id = str(uuid.uuid4())

    def to_payload(
        self, 
        issuer: str, 
        audience: str = "AuctionNetwork"
    ) -> dict[str, Any]:
        if not self.subject:
            raise ValueError("JWT subject cannot be empty")
        return {
            # The `iss` (Issuer) claim.
            "iss": issuer,
            # The `sub` (Subject) claim.
            "sub": self.subject,
            # The `aud` (Audience) claim.
            "aud": audience,
            # The `exp` (Expiration Time) claim.
            "exp": int(self.expiration.timestamp()),
            # The `nbf` (Not Before) claim.
            "nbf": int(self.not_before.timestamp()),
            # The `iat` (Issued At) claim.
            "iat": int(self.issued_at.timestamp()),
            # The `jti` (JWT ID) claim.
            "jti": self.jwt_id
        }
