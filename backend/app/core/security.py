from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )

    payload = {
        "sub": str(user_id),
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
