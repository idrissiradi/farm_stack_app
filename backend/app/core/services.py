from http import HTTPStatus

from fastapi import Request, HTTPException
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.auth.models import UserInResponse
from app.core.security import decode_access_token
from app.auth.selectors import get_user_by_id


async def is_authenticated(request: Request) -> UserInResponse:
    """Get authenticated user"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Invalid authorization"
        )
    user_id = decode_access_token(access_token)
    user = await get_user_by_id(request, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


def create_aliased_response(model: BaseModel) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(model, by_alias=True))
