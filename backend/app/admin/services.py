import random
import string
from http import HTTPStatus
from typing import Any, List, Optional

from fastapi import Request, HTTPException
from slugify import slugify
from pydantic import EmailStr
from fastapi.encoders import jsonable_encoder

from app.auth.models import UserInDB, UserModel
from app.admin.models import (
    Media,
    Property,
    Reservation,
    PropertyInDB,
    PropertyInCreate,
    PropertyInUpdate,
    ReservationModel,
)
from app.auth.selectors import get_user
from app.admin.selectors import get_property_by_slug, get_reservation_by_id


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


async def create_property(
    request: Request, property: PropertyInCreate, user: UserModel
) -> Optional[Property]:
    """Create new Post"""
    new_doc = property.dict()
    slug = slugify(property.title)
    slug_exist = await get_property_by_slug(request, slug)
    if slug_exist:
        slug = "{slug}-{randstr}".format(slug=slug, randstr=random_string_generator())

    media_list: List[Media] = []
    for row in property.media:
        media_list.append(row)

    new_doc["media"] = media_list
    new_doc["owner"] = user
    new_doc["slug"] = slug
    db_property = PropertyInDB(**new_doc)
    data = jsonable_encoder(db_property)
    new_property = await request.app.mongodb.Properties.insert_one(data)
    created_property = await request.app.mongodb.Properties.find_one(
        {"_id": new_property.inserted_id}
    )
    return Property(**created_property)


async def check_property_owner(
    request: Request, slug: str, email: EmailStr = ""
) -> Any:
    """Check user is the owner"""
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


async def check_staff_permission(request: Request, user: UserModel, slug: str) -> Any:
    """Check staff permission"""
    searched_property = await get_property_by_slug(request, slug)
    db_user: UserInDB = get_user(request, user.email)
    staff = request.app.mongodb.Staff.find_one(
        {"user_id": db_user.id, "property_id": searched_property.id}
    )
    if not staff:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You have no permission for modifying this article",
        )


async def check_user_permission(
    request: Request, user: UserModel, slug: str = ""
) -> Any:
    """Check user permission"""
    if not user.role == "owner" and not user.role == "staff":
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You have no permission for modifying this article",
        )
    if user.role == "staff":
        await check_staff_permission(request, user, slug)


async def update_property_by_slug(
    request: Request, slug: str, property: PropertyInUpdate
) -> Property:
    db_property = await get_property_by_slug(request, slug)
    if not db_property:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Something went wrong / Bad request",
        )
    if property.title:
        new_slug = slugify(property.title)
        slug_exist = await get_property_by_slug(request, new_slug)
        if slug_exist:
            new_slug = "{slug}-{randstr}".format(
                slug=slug, randstr=random_string_generator()
            )
        db_property.slug = new_slug
        db_property.title = property.title

    db_property.is_active = property.is_active
    db_property.description = (
        property.description if property.description else db_property.description
    )
    db_property.price = property.price if property.price else db_property.price
    db_property.address = property.address if property.address else db_property.address
    db_property.media = property.media if property.media else db_property.media
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
                "address": jsonable_encoder(db_property.address),
                "media": jsonable_encoder(db_property.media),
            }
        },
    )
    updated_property = await get_property_by_slug(request, db_property.slug)
    return updated_property


async def delete_property_by_slug(
    request: Request, slug: str, email: EmailStr = ""
) -> Any:
    property = await get_property_by_slug(request, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Something went wrong / Bad request",
        )
    await request.app.mongodb.Properties.delete_one(
        {"slug": slug, "owner.email": email}
    )


async def create_reservation(
    request: Request, reservation: ReservationModel, slug: str
) -> Reservation:
    property = await get_property_by_slug(request, slug)
    if property:
        db_reservation = Reservation(property_id=property.id, **reservation.dict())
        data = jsonable_encoder(db_reservation)
        new_reservation = await request.app.mongodb.Reservations.insert_one(data)
        created_reservation = await get_reservation_by_id(
            request=request, id=new_reservation.inserted_id
        )
        return created_reservation
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


async def update_owner_reservation(
    request: Request, reservation: Reservation
) -> Reservation:
    db_reservation = await get_reservation_by_id(request, reservation.id)
    if db_reservation:
        db_reservation.date_start = (
            reservation.date_start
            if reservation.date_start
            else db_reservation.date_start
        )
        db_reservation.date_end = (
            reservation.date_end if reservation.date_end else db_reservation.date_end
        )
        db_reservation.body = (
            reservation.body if reservation.body else db_reservation.body
        )
        await request.app.mongodb.Reservations.update_one(
            {"_id": reservation.id},
            {
                "$set": {
                    "date_start": db_reservation.date_start,
                    "date_end": db_reservation.date_end,
                    "body": db_reservation.body,
                }
            },
        )
        updated_reservation = await get_reservation_by_id(request, reservation.id)
        return updated_reservation


async def delete_reservation_by_property_slug(request: Request, slug: str) -> Any:
    property = await get_property_by_slug(request, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Something went wrong / Bad request",
        )
    await request.app.mongodb.Reservations.delete_many({"property_id": property.id})


async def delete_reservation(request: Request, id: str) -> Any:
    reservation = await get_reservation_by_id(request, id)
    if reservation:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Something went wrong / Bad request",
        )
    await request.app.mongodb.Reservations.delete_one({"_id": id})
