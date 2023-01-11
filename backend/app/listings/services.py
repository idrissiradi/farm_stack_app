from typing import Any, Optional
from odmantic import AIOEngine
import random
import string
from app.auth.models import UserBase
from fastapi import HTTPException
from http import HTTPStatus

from app.listings.models import Property, PropertyInCreate
from slugify import slugify

from app.listings.selectors import get_property_by_slug


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


async def check_user_permission(
    engine: AIOEngine, user: UserBase, slug: str = ""
) -> Any:
    """Check user permission"""
    if not user.is_active and not user.is_verified:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You have no permission for creating an article",
        )


async def create_property(
    engine: AIOEngine, property: PropertyInCreate, user: UserBase
) -> Optional[Property]:
    """Create new Post"""
    slug = slugify(property.title)
    slug_exist = await get_property_by_slug(engine, slug)
    if slug_exist:
        slug = "{slug}-{randstr}".format(slug=slug, randstr=random_string_generator())

    db_property = Property(**property.dict(), owner=user, slug=slug)
    await engine.save(db_property)
    created_property = await get_property_by_slug(engine, slug)
    return created_property
