from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.router import api_router
from app.core.audit import write_audit_log
from app.core.config import get_settings
from app.core.database import SessionLocal, init_database
from app.core.logging import setup_logging
from app.core.rate_limiter import RateLimiter
from app.core.security import decode_token
from app.core.telemetry import REQUEST_COUNT, observe_request
from app.services.auth_service import AuthService

settings = get_settings()
rate_limiter = RateLimiter()
auth_service = AuthService()


def create_app() -> FastAPI:
    setup_logging()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("Bootstrapping database and break-glass user")
        await init_database()
        async with SessionLocal() as session:
            await auth_service.bootstrap_break_glass_user(session)
        yield

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def telemetry_middleware(request: Request, call_next):
        rate_limiter.check(request)
        with observe_request(request.url.path, request.method):
            response = await call_next(request)
        REQUEST_COUNT.labels(
            path=request.url.path,
            method=request.method,
            status=str(response.status_code),
        ).inc()
        return response

    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        response = await call_next(request)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.url.path.startswith("/api/v1"):
            auth_header = request.headers.get("authorization", "")
            user_id = None
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                try:
                    payload = decode_token(token)
                    uid = payload.get("uid")
                    if isinstance(uid, int):
                        user_id = uid
                    elif isinstance(uid, str) and uid.isdigit():
                        user_id = int(uid)
                except Exception:
                    user_id = None
            async with SessionLocal() as session:
                await write_audit_log(
                    session=session,
                    user_id=user_id,
                    action=request.method.lower(),
                    resource_type=request.url.path,
                    resource_id="-",
                    details={"status_code": response.status_code},
                )
        return response

    @app.get("/metrics")
    async def metrics() -> Response:
        content = generate_latest()
        return Response(content=content, media_type=CONTENT_TYPE_LATEST)

    app.include_router(api_router)
    return app


app = create_app()
