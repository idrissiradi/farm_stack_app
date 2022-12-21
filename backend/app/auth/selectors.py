from typing import Optional

from fastapi import Request
from pydantic import EmailStr

from app.auth.models import (
    UserBase,
    UserInDB,
    ResetInDB,
    UserModel,
    VerifyInDB,
    UserTokenInDB,
)


async def get_user(request: Request, email: EmailStr) -> Optional[UserInDB]:
    """Get user"""
    user = await request.app.mongodb.Users.find_one({"email": email})
    if user:
        return UserInDB(**user)
    return None


async def get_user_by_email(request: Request, email: EmailStr) -> Optional[UserModel]:
    """Get user by email"""
    user = await request.app.mongodb.Users.find_one({"email": email}, {"password": 0})
    if user:
        return UserModel(**user)
    return None


async def get_user_by_id(request: Request, id: str) -> Optional[UserBase]:
    """Get user by id"""
    user = await request.app.mongodb.Users.find_one({"_id": id}, {"password": 0})
    if user:
        return UserBase(**user)
    return None


async def get_verify_email(request: Request, token: str) -> Optional[VerifyInDB]:
    """Get verify email by token"""
    verify = await request.app.mongodb.UserVerify.find_one({"token": token})
    if verify:
        return VerifyInDB(**verify)
    return None


async def get_user_token(request: Request, token: str) -> Optional[UserTokenInDB]:
    """Get user token"""
    token = await request.app.mongodb.UserToken.find_one({"token": token})
    if token:
        return UserTokenInDB(**token)
    return None


async def get_user_reset(request: Request, token: str) -> Optional[ResetInDB]:
    """Get user reset"""
    user_reset = await request.app.mongodb.UserReset.find_one({"token": token})
    if user_reset:
        return ResetInDB(**user_reset)
    return None
