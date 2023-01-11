import random
import string
import datetime
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Response, HTTPException, BackgroundTasks
from odmantic import ObjectId, AIOEngine
from pydantic import EmailStr

from app.auth.utils import send_email, verify_password
from app.auth.models import (
    User,
    UserBase,
    ResetInDB,
    UserInUpdate,
    VerifyInDB,
    UserInCreate,
    UserTokenInDB,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.selectors import get_user_by_email


async def create_user(engine: AIOEngine, user: UserInCreate) -> Optional[UserBase]:
    """Create new user"""
    user.change_password(user.password)
    username = user.email.split("@")[0]
    db_user = User(**user.dict(), username=username)
    await engine.configure_database([User])
    await engine.save(db_user)
    created_user = await get_user_by_email(engine, user.email)
    return created_user


async def send_verify_email(
    email: EmailStr, engine: AIOEngine, task: BackgroundTasks
) -> Any:
    """Send verification email"""
    user = await get_user_by_email(engine, email)
    full_name = user.first_name + " " + user.last_name
    email: EmailStr = user.email
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
    )

    db_verify = VerifyInDB(email=email, token=token)
    await engine.save(db_verify)

    absurl = settings.SERVER_HOST + "api/auth/verify" + "?token=" + str(token)
    redirect_url = settings.FRONTEND_URL

    email_body = (
        "<h1> "
        + "Hi "
        + str(full_name)
        + " Use the link below to verify your email"
        + "</h1> <br>"
        + "<p>"
        + absurl
        + "&redirect_url="
        + redirect_url
        + "/login"
        + "</p>"
    )
    email_from = settings.EMAILS_FROM_EMAIL
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    data = {
        "email_body": email_body,
        "to_email": email,
        "email_subject": "Verify your email",
        "from": email_from,
        "smtp": smtp_options,
    }
    print("sending mail...")
    return task.add_task(send_email, data)


async def authenticate(
    engine: AIOEngine, email: EmailStr, password: str
) -> Optional[User]:
    """Check authenticated user"""
    user = await get_user_by_email(engine, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def generate_token(engine: AIOEngine, id: ObjectId, response: Response) -> str:
    """Generate Refresh/Access token"""
    access_token = create_access_token(id.__str__())
    refresh_token = create_refresh_token(id.__str__())
    user_token = UserTokenInDB(
        user_id=id.__str__(),
        token=refresh_token,
        expired_at=datetime.datetime.utcnow()
        + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS),
    )
    async with engine.session() as session:
        await session.remove(UserTokenInDB, UserTokenInDB.user_id == id.__str__())
        await session.save(user_token)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        expires=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        expires=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(20)
    )
    return token


async def generate_access_token(
    engine: AIOEngine, refresh_token: str, response: Response
) -> str:
    """Generate New Access token"""
    user_id = decode_refresh_token(refresh_token)
    user_token = await engine.find_one(UserTokenInDB, UserTokenInDB.user_id == user_id)
    if not user_token:
        raise HTTPException(HTTPStatus.FORBIDDEN, "unauthenticated")

    access_token = create_access_token(user_id)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        expires=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(20)
    )
    return token


async def send_reset_password(
    engine: AIOEngine, email: str, background_tasks: BackgroundTasks
):
    """Send reset password email"""

    user = await get_user_by_email(engine, email)
    full_name = user.first_name + " " + user.last_name
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
    )
    reset = ResetInDB(email=user.email, token=token)
    async with engine.session() as session:
        await session.remove(ResetInDB, ResetInDB.email == user.email)
        await session.save(reset)

    url = settings.FRONTEND_URL + "/reset" + "?token=" + str(token)
    email_body = (
        "<h1> "
        + "Hi "
        + str(full_name)
        + " Use the link below to reset your password"
        + "</h1> <br>"
        + "<p>"
        + url
        + "</p>"
    )
    email_from = settings.EMAILS_FROM_EMAIL
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    data = {
        "email_body": email_body,
        "to_email": email,
        "email_subject": "Reset your password",
        "from": email_from,
        "smtp": smtp_options,
    }
    return background_tasks.add_task(send_email, data)


async def update_user_profile(
    engine: AIOEngine, data: UserInUpdate, user: UserBase
) -> UserBase:
    user.first_name = data.first_name if data.first_name else user.first_name
    user.last_name = data.last_name if data.last_name else user.last_name
    user.role = data.role if data.role else user.role
    await engine.save(user)
    updated_user = await get_user_by_email(engine, user.email)
    return updated_user
