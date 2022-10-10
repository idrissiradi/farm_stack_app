from typing import Optional

from rich import print
from fastapi import Request
from pydantic import EmailStr

from app.auth.models import VerifyInDB, UserTokenInDB, UserInResponse


async def get_user(request: Request, email: EmailStr) -> Optional[UserInResponse]:
    """Get user"""
    user = await request.app.mongodb.Users.find_one({"email": email})
    return user


async def get_user_by_email(
    request: Request, email: EmailStr
) -> Optional[UserInResponse]:
    """Get user by email"""
    user = await request.app.mongodb.Users.find_one({"email": email}, {"password": 0})
    return user


async def get_verify_email(request: Request, token: str) -> Optional[VerifyInDB]:
    """Get verify email by token"""
    verify = await request.app.mongodb.UserVerify.find_one({"token": token})
    return verify


async def get_user_token(request: Request, token: str) -> Optional[UserTokenInDB]:
    """Get user token"""
    token = await request.app.mongodb.UserToken.find_one({"token": token})
    return token
