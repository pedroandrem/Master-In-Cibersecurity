import jwt
from jwt import PyJWTError, ExpiredSignatureError, ImmatureSignatureError, InvalidIssuerError, InvalidAudienceError

class JWTValidator:

    def __init__(self, key, algorithms=None, expected_issuer=None, expected_audience=None):
        self.key = key
        self.algorithms = algorithms or ["HS256", "RS256", "ES256"]
        self.expected_issuer = expected_issuer
        self.expected_audience = expected_audience
        self.used_jtis = set()  # Simple in-memory replay prevention

    def validate(self, token, client_info=None):
        if not token:
            raise ValueError(f"Missing JWT from {client_info or 'unknown client'}")

        try:
            payload = jwt.decode(
                token,
                self.key,
                algorithms=self.algorithms,
                audience=self.expected_audience,
                issuer=self.expected_issuer,
                options={"require": ["exp", "iat", "nbf", "jti", "sub"]}
            )

            jti = payload["jti"]
            if jti in self.used_jtis:
                raise ValueError(f"Replay attack detected from {client_info or 'unknown client'}, jti={jti}")
            self.used_jtis.add(jti)

            return payload

        except ExpiredSignatureError:
            raise ValueError(f"JWT expired from {client_info or 'unknown client'}")
        except ImmatureSignatureError:
            raise ValueError(f"JWT not valid yet (nbf) from {client_info or 'unknown client'}")
        except InvalidIssuerError:
            raise ValueError(f"Invalid issuer from {client_info or 'unknown client'}")
        except InvalidAudienceError:
            raise ValueError(f"Invalid audience from {client_info or 'unknown client'}")
        except PyJWTError as e:
            raise ValueError(f"Invalid JWT from {client_info or 'unknown client'}: {e}")
