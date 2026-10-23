from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import config
from app.auth import users
from app.auth.deps import get_current_user
from app.ratelimit import limiter
from app.routers import auth, v1, v2


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the first admin from env vars (users live in memory, so this
    # runs on every start). Without it nobody could create other users.
    if config.ADMIN_PASSWORD:
        users.create(config.ADMIN_USERNAME, config.ADMIN_PASSWORD, role="admin")
    yield


app = FastAPI(title="Simple Items API", lifespan=lifespan)

# Rate limiting: default limit on every route (via middleware), plus a stricter
# one on /auth/token. Over the limit -> HTTP 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Every item route requires a valid JWT. Role checks live on individual routes.
require_login = Depends(get_current_user)

app.include_router(auth.router)

# Which version answers on the plain, unversioned URLs (e.g. /items).
# To promote a new version, change this one line.
CURRENT_VERSION = v2

# Announced retirement date for v1 (sent in the Sunset header)
V1_SUNSET = "Wed, 31 Mar 2027 23:59:59 GMT"


def add_v1_deprecation_headers(response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = V1_SUNSET
    response.headers["Link"] = '</v2/items>; rel="successor-version"'


# Explicit versions: stable contracts people can pin to
app.include_router(
    v1.router,
    prefix="/v1",
    tags=["v1 (deprecated)"],
    deprecated=True,  # strikethrough in /docs
    dependencies=[require_login, Depends(add_v1_deprecation_headers)],
)
app.include_router(v2.router, prefix="/v2", tags=["v2"], dependencies=[require_login])

# Unversioned URLs: same code as the current version, hidden from /docs
app.include_router(
    CURRENT_VERSION.router, include_in_schema=False, dependencies=[require_login]
)


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.get("/health")
@limiter.exempt  # deploy health checks and load balancers must never be throttled
def health():
    return {"status": "ok"}
