from http import HTTPStatus
from typing import Any, Optional

from fastapi import Request, HTTPException
from slugify import slugify
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

from app.auth.models import UserModel
from app.property.models import (
    Property,
    PropertyInDB,
    PropertyInCreate,
    PropertyInUpdate,
)
from app.property.selectors import get_property_by_slug


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


async def check_property_owner(
    request: Request, slug: str, email: EmailStr = ""
) -> Any:
    """Check user permission"""
    searched_property = await get_property_by_slug(request, slug)
    if not searched_property:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Property with slug '{slug}' not found",
        )
    if searched_property.owner.email != email:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You have no permission for modifying this article",
        )


async def update_property_by_slug(
    request: Request, slug: str, property: PropertyInUpdate
) -> Property:
    db_property = await get_property_by_slug(request, slug)
    if property.title:
        db_property.slug = slugify(property.title)
        db_property.title = property.title
    db_property.description = (
        property.description if property.description else db_property.description
    )
    db_property.is_active = (
        property.is_active if property.is_active else db_property.is_active
    )
    db_property.price = property.price if property.price else db_property.price
    db_property.property_type = (
        property.property_type if property.property_type else db_property.property_type
    )
    await request.app.mongodb.Properties.update_one(
        {"slug": slug},
        {
            "$set": {
                "title": db_property.title,
                "slug": db_property.slug,
                "description": db_property.description,
                "is_active": db_property.is_active,
                "price": db_property.price,
                "Property_type": db_property.property_type,
            }
        },
    )
    return db_property


async def delete_property_by_slug(
    request: Request, slug: str, email: EmailStr = ""
) -> Any:
    await request.app.mongodb.Properties.delete_one(
        {"slug": slug, "owner_email": email}
    )
