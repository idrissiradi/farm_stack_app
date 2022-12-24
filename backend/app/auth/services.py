import random
import string
import datetime
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Request, Response, HTTPException, BackgroundTasks
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

from app.auth.utils import send_email, verify_password
from app.auth.models import (
    UserInDB,
    ResetInDB,
    UserModel,
    VerifyInDB,
    UserInCreate,
    UserInUpdate,
    UserTokenInDB,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.selectors import get_user, get_user_by_email


async def create_user(request: Request, user: UserInCreate) -> Optional[UserModel]:
    """Create new user"""
    user.change_password(user.password)
    username = user.email.split("@")[0]
    db_user = UserInDB(**user.dict(), username=username)
    data = jsonable_encoder(db_user)
    new_user = await request.app.mongodb.Users.insert_one(data)
    created_user = await request.app.mongodb.Users.find_one(
        {"_id": new_user.inserted_id}, {"password": 0, "_id": 0}
    )
    return UserModel(**created_user)


async def send_verify_email(
    email: EmailStr, request: Request, background_tasks: BackgroundTasks
) -> Any:
    """Send verification email"""
    user = await get_user_by_email(request, email)
    full_name = user.first_name + " " + user.last_name
    email: EmailStr = user.email
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
    )

    db_verify = VerifyInDB(email=email, token=token)
    data = jsonable_encoder(db_verify)
    await request.app.mongodb.UserVerify.insert_one(data)

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
    return background_tasks.add_task(send_email, data)


async def authenticate(
    request: Request, email: EmailStr, password: str
) -> Optional[UserInDB]:
    """Check authenticated user"""
    user = await get_user(request, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def generate_token(id: int, request: Request, response: Response) -> str:
    """Generate Refresh/Access token"""

    access_token = create_access_token(id)
    refresh_token = create_refresh_token(id)

    user_token = UserTokenInDB(
        user_id=id,
        token=refresh_token,
        expired_at=datetime.datetime.utcnow()
        + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS),
    )

    data = jsonable_encoder(user_token)
    await request.app.mongodb.UserToken.delete_many({"user_id": id})
    await request.app.mongodb.UserToken.insert_one(data)

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


async def generate_access_token(request: Request, response: Response) -> str:
    """Generate Access token"""

    refresh_token = request.cookies.get("refresh_token")
    user_id = decode_refresh_token(refresh_token)
    user_token = await request.app.mongodb.UserToken.find_one({"user_id": user_id})
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
    email: str, background_tasks: BackgroundTasks, request: Request
):
    """Send reset password email"""

    user = await get_user_by_email(request, email)
    full_name = user.first_name + " " + user.last_name
    token = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
    )
    reset = ResetInDB(email=user.email, token=token)
    data = jsonable_encoder(reset)
    await request.app.mongodb.UserReset.delete_one({"email": user.email})
    await request.app.mongodb.UserReset.insert_one(data)

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
    request: Request, data: UserInUpdate, user: UserModel
) -> UserModel:
    user.first_name = data.first_name if data.first_name else user.first_name
    user.last_name = data.last_name if data.last_name else user.last_name
    user.role = data.role if data.role else user.role
    await request.app.mongodb.Users.update_one(
        {"email": user.email},
        {
            "$set": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            }
        },
    )
    updated_user = await get_user_by_email(request, user.email)
    return updated_user
