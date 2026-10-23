"""FastAPI dependencies: authentication (who are you?) and authorization (may you?)."""
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import users
from app.auth.security import decode_access_token

# Makes the "Authorize" button appear in /docs and reads the Bearer token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        username = decode_access_token(token)
    except jwt.PyJWTError:
        raise _credentials_error
    user = users.get(username)
    # Looking the user up on every request means disabling a user or
    # changing their role takes effect immediately, not at token expiry.
    if user is None or user["disabled"]:
        raise _credentials_error
    return user


def require_role(*roles: str):
    def checker(user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")
        return user

    return checker
