"""Password hashing and JWT creation/validation."""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app import config


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:  # e.g. password longer than bcrypt's 72-byte limit
        return False


# Used to burn the same CPU time when a username doesn't exist,
# so response time doesn't reveal which usernames are valid.
DUMMY_HASH = hash_password("not-a-real-password")


def create_access_token(username: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """Return the username in the token, or raise jwt.PyJWTError."""
    payload = jwt.decode(
        token,
        config.JWT_SECRET,
        algorithms=[config.JWT_ALGORITHM],  # pin the algorithm
        options={"require": ["exp", "sub"]},
    )
    return payload["sub"]
