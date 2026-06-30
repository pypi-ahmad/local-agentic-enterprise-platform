from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import Role, User


class AuthService:
    """User authentication and break-glass bootstrap."""

    async def bootstrap_break_glass_user(self, session: AsyncSession) -> User:
        settings = get_settings()
        target_email = f"{settings.break_glass_username}@example.com"
        result = await session.execute(select(User).where(User.username == settings.break_glass_username))
        user = result.scalar_one_or_none()
        if user:
            should_update = False
            if user.email != target_email:
                user.email = target_email
                should_update = True
            if not verify_password(settings.break_glass_password, user.hashed_password):
                user.hashed_password = hash_password(settings.break_glass_password)
                should_update = True
            if should_update:
                await session.commit()
                await session.refresh(user)
            return user

        user = User(
            email=target_email,
            username=settings.break_glass_username,
            full_name="Local Break Glass Admin",
            hashed_password=hash_password(settings.break_glass_password),
            role=Role.ORG_ADMIN,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def authenticate_local(self, session: AsyncSession, username: str, password: str) -> User | None:
        result = await session.execute(select(User).where(User.username == username, User.is_active.is_(True)))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(
        self,
        session: AsyncSession,
        email: str,
        username: str,
        full_name: str,
        password: str,
        role: str,
    ) -> User:
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=Role(role),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
