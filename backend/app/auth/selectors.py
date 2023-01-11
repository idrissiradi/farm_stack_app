from typing import Optional

from odmantic import AIOEngine, ObjectId
from pydantic import EmailStr

from app.auth.models import User, UserBase, ResetInDB, VerifyInDB, UserTokenInDB


async def get_user_by_email(engine: AIOEngine, email: EmailStr) -> Optional[User]:
    """Get user by email"""
    user = await engine.find_one(User, User.email == email)
    if user:
        return user
    return None


async def get_user_by_id(engine: AIOEngine, id: str) -> Optional[User]:
    """Get user by id"""
    user_id = ObjectId(id)
    user = await engine.find_one(User, User.id == user_id)
    if user:
        return user
    return None


async def get_verify_email(engine: AIOEngine, token: str) -> Optional[VerifyInDB]:
    """Get verify email by token"""
    verify = await engine.find_one(VerifyInDB, VerifyInDB.token == token)
    if verify:
        return verify
    return None


async def get_user_reset(engine: AIOEngine, token: str) -> Optional[ResetInDB]:
    """Get user (reset password) by token"""
    user_reset = await engine.find_one(ResetInDB, ResetInDB.token == token)
    if user_reset:
        return user_reset
    return None
