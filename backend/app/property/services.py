import random
import string
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


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


async def create_post(
    request: Request, property: PropertyInCreate, user: UserModel
) -> Optional[Property]:
    """Create new Post"""
    slug = slugify(property.title)
    slug_exist = await get_property_by_slug(request, slug)
    if slug_exist:
        slug = "{slug}-{randstr}".format(slug=slug, randstr=random_string_generator())
    db_property = PropertyInDB(**property.dict(), owner=user, slug=slug)
    data = jsonable_encoder(db_property)
    new_property = await request.app.mongodb.Properties.insert_one(data)
    created_property = await request.app.mongodb.Properties.find_one(
        {"_id": new_property.inserted_id}
    )
    return Property(**created_property)


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
    print(db_property.is_active)
    if property.title:
        new_slug = slugify(property.title)
        slug_exist = await get_property_by_slug(request, new_slug)
        if slug_exist:
            new_slug = "{slug}-{randstr}".format(
                slug=slug, randstr=random_string_generator()
            )
        db_property.slug = new_slug
        db_property.title = property.title

    if property.is_active != db_property.is_active:
        db_property.is_active = property.is_active

    db_property.is_active = db_property.is_active

    db_property.description = (
        property.description if property.description else db_property.description
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
                "property_type": db_property.property_type,
            }
        },
    )
    updated_property = await get_property_by_slug(request, db_property.slug)
    return updated_property


async def delete_property_by_slug(
    request: Request, slug: str, email: EmailStr = ""
) -> Any:
    await request.app.mongodb.Properties.delete_one(
        {"slug": slug, "owner_email": email}
    )
