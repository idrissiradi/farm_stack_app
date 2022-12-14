import datetime
from http import HTTPStatus
from typing import Optional

import jwt
from jwt import PyJWTError
from fastapi import Depends, Request, HTTPException
from odmantic import AIOEngine

from app.auth.models import UserBase
from app.core.config import settings
from app.core.services import get_db
from app.auth.selectors import get_user_by_id


def _get_authorization_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials"
        )
    return token


async def _get_current_user(
    token: str = Depends(_get_authorization_token),
    engine: AIOEngine = Depends(get_db),
) -> UserBase:
    user_id = decode_access_token(token)
    user = await get_user_by_id(engine, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


def _get_authorization_token_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return ""
    return _get_authorization_token(request)


async def _get_current_user_optional(
    engine: AIOEngine = Depends(get_db),
    token: str = Depends(_get_authorization_token_optional),
) -> Optional[UserBase]:
    if token:
        return await _get_current_user(engine, token)
    return None


def get_current_user_authorizer(*, required: bool = True) -> Optional[UserBase]:
    if required:
        return _get_current_user
    else:
        return _get_current_user_optional


def create_access_token(id: str) -> str:
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


def create_refresh_token(id: str):
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


def decode_refresh_token(token: str):
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
