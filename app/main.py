from fastapi import Depends, FastAPI, Response

from app.routers import v1, v2

app = FastAPI(title="Simple Items API")

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
    dependencies=[Depends(add_v1_deprecation_headers)],  # warning headers
)
app.include_router(v2.router, prefix="/v2", tags=["v2"])

# Unversioned URLs: same code as the current version, hidden from /docs
app.include_router(CURRENT_VERSION.router, include_in_schema=False)


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.get("/health")
def health():
    return {"status": "ok"}
