from typing import Any, Optional

from fastapi import Request, Response, HTTPException
from slugify import slugify
from fastapi.encoders import jsonable_encoder

from app.auth.models import UserModel
from app.post.models import Post, PostInDB, PostInCreate


async def create_post(
    request: Request, post: PostInCreate, user: UserModel
) -> Optional[Post]:
    """Create new Post"""
    db_post = jsonable_encoder(
        PostInDB(owner=user, slug=slugify(post.title), **post.dict())
    )
    new_post = await request.app.mongodb.Posts.insert_one(db_post)
    created_post = await request.app.mongodb.Posts.find_onr(
        {"_id": new_post.inserted_id}
    )
    return created_post
