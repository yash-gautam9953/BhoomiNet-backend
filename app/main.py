import logging
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, certificate, issuer
from app.core.config import settings
from app.db.base import create_db_and_tables

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("app.api")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend APIs for issuer onboarding and certificate metadata/IPFS operations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_origin_regex=settings.CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    start = time.perf_counter()

    logger.info("request_start id=%s method=%s path=%s", request_id, request.method, request.url.path)

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "request_error id=%s method=%s path=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request_end id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception method=%s path=%s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(issuer.router, prefix="/issuer", tags=["Issuer"])
app.include_router(certificate.router, prefix="/certificate", tags=["Certificate"])
