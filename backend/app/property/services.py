from typing import Any, Optional

from fastapi import Request, Response, HTTPException
from slugify import slugify
from fastapi.encoders import jsonable_encoder

from app.auth.models import UserModel
from app.property.models import Property, PropertyInDB, PropertyInCreate


async def create_post(
    request: Request, post: PropertyInCreate, user: UserModel
) -> Optional[Property]:
    """Create new Post"""
    db_property = jsonable_encoder(
        PropertyInDB(owner=user, slug=slugify(post.title), **post.dict())
    )
    new_property = await request.app.mongodb.Properties.insert_one(db_property)
    created_property = await request.app.mongodb.Properties.find_onr(
        {"_id": new_property.inserted_id}
    )
    return created_property
