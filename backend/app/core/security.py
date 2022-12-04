import datetime
from http import HTTPStatus

import jwt
from jwt import PyJWTError
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Invalid token or expired token.",
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_access_token(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


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
