"""Login, current-user and admin user-management endpoints."""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app import config
from app.auth import users
from app.auth.deps import get_current_user, require_role
from app.auth.security import DUMMY_HASH, create_access_token, verify_password
from app.ratelimit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(..., min_length=8, max_length=72)  # 72 = bcrypt limit
    role: Literal["user", "admin"] = "user"


class UserOut(BaseModel):
    username: str
    role: str


@router.post("/token", response_model=Token)
@limiter.limit(config.LOGIN_RATE_LIMIT)  # brute-force protection
def login(request: Request, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users.get(form.username)
    # Always run one bcrypt check so timing doesn't leak whether the user exists.
    password_ok = verify_password(
        form.password, user["password_hash"] if user else DUMMY_HASH
    )
    if user is None or user["disabled"] or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(user["username"]),
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserOut)
def me(user: Annotated[dict, Depends(get_current_user)]):
    return user


@router.post(
    "/users",
    status_code=201,
    response_model=UserOut,
    dependencies=[Depends(require_role("admin"))],
)
def create_user(payload: UserCreate):
    user = users.create(payload.username, payload.password, payload.role)
    if user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    return user
