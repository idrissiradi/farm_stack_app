import datetime
from http import HTTPStatus
from typing import Optional

import jwt
from jwt import PyJWTError
from fastapi import Depends, Request, HTTPException

from app.auth.models import UserModel
from app.core.config import settings
from app.auth.selectors import get_user_by_id


def _get_authorization_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials"
        )
    return token


async def _get_current_user(
    request: Request, token: str = Depends(_get_authorization_token)
) -> UserModel:
    user_id = decode_access_token(token)
    user = await get_user_by_id(request, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


def _get_authorization_token_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return ""
    return _get_authorization_token(request)


async def _get_current_user_optional(
    request: Request,
    token: str = Depends(_get_authorization_token_optional),
) -> Optional[UserModel]:
    if token:
        return await _get_current_user(request, token)
    return None


def get_current_user_authorizer(*, required: bool = True):
    if required:
        return _get_current_user
    else:
        return _get_current_user_optional


def create_access_token(id: int) -> str:
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
            "iat": datetime.datetime.utcnow(),
        },
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        return payload["user_id"]
    except PyJWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def create_refresh_token(id):
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS),
            "iat": datetime.datetime.utcnow(),
        },
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_refresh_token(token):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        return payload["user_id"]
    except PyJWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
        )
