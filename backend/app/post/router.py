from http import HTTPStatus
from typing import Any

from fastapi import Body, Request, Response, APIRouter, HTTPException

from app.post.models import (
    PostInCreate,
    PostInUpdate,
    PostInResponse,
    ManyPostsInResponse,
)
from app.core.services import is_authenticated, create_aliased_response
from app.post.services import create_post

router = APIRouter(prefix="/post")


@router.post("/posts", response_model=PostInResponse, status_code=HTTPStatus.CREATED)
async def new_post(request: Request, post: PostInCreate = Body(..., embed=True)) -> Any:
    user = await is_authenticated(request)
    if user:
        if not user["is_active"] and not user["is_verified"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="User not allowed"
            )

        new_post = create_post(request, post, user)
        if new_post:
            return create_aliased_response(new_post)
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )
