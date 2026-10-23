"""Settings read from environment variables (never hard-code secrets)."""
import os

JWT_SECRET = os.environ.get("JWT_SECRET", "")
if len(JWT_SECRET) < 32:
    raise RuntimeError(
        "JWT_SECRET must be set to a random string of at least 32 characters. "
        "Generate one with: openssl rand -hex 32"
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# The first admin account, created at startup if it doesn't exist yet.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Rate limits, per client IP. Format: "<count>/<second|minute|hour|day>"
LOGIN_RATE_LIMIT = os.environ.get("LOGIN_RATE_LIMIT", "5/minute")
DEFAULT_RATE_LIMIT = os.environ.get("DEFAULT_RATE_LIMIT", "120/minute")
