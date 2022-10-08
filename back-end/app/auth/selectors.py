from rich import print
from fastapi import Request
from pydantic import EmailStr

from app.auth.models import VerifyInDB, UserInResponse


async def get_user_by_email(request: Request, email: EmailStr) -> UserInResponse:
    """Get user by email"""
    user = await request.app.mongodb.Users.find_one({"email": email}, {"password": 0})
    return user


async def get_verify_email(request: Request, token: str) -> VerifyInDB:
    """Get verify email by token"""
    verify = await request.app.mongodb.Verify.find_one({"token": token})
    return verify
