from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token
from app.dependencies import db_session, get_current_user, require_roles
from app.models import Role, User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserView
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(db_session)) -> TokenResponse:
    user = await service.authenticate_local(session, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.username, roles=[user.role.value], user_id=user.id)
    return TokenResponse(access_token=token, roles=[user.role.value])


@router.post("/users", response_model=UserView)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(require_roles(Role.ORG_ADMIN)),
) -> UserView:
    user = await service.create_user(
        session=session,
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
    )
    return UserView.model_validate(user)


@router.get("/me", response_model=UserView)
async def me(user: User = Depends(get_current_user)) -> UserView:
    return UserView.model_validate(user)


@router.get("/google/url")
async def google_oauth_url() -> dict:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
    }
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"}


@router.get("/google/callback")
async def google_oauth_callback(code: str = Query(..., min_length=5)) -> dict:
    return {
        "message": "OAuth callback received",
        "authorization_code": code,
        "next_step": "Exchange code for tokens in secure backend secret store workflow.",
    }
