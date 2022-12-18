from typing import List, Optional

from fastapi import Request
from pydantic import EmailStr

from app.auth.models import UserModel
from app.property.models import Property, PropertyFilterParams


async def get_properties(
    request: Request, filters: PropertyFilterParams
) -> Optional[List[Property]]:
    """Get feed properties"""
    properties: List[Property] = []
    properties_docs = request.app.mongodb.Properties.find(
        {"owner_username": filters.owner},
        {"type": filters.type},
        limit=filters.limit,
        skip=filters.offset,
    ).sort("created_at")
    async for row in properties_docs:
        properties.append(Property(**row))
    return properties


async def get_property_by_slug(request: Request, slug: str) -> Property:
    """Get property by slug"""
    property = await request.app.mongodb.Properties.find_one({"slug": slug})
    return property


async def get_user_properties(
    request: Request, username: str, limit: int, offset: int
) -> Optional[List[Property]]:
    """Get user properties"""
    properties: List[Property] = []
    properties_docs = request.app.mongodb.Properties.find(
        {"owner_username": username}, limit=limit, skip=offset
    ).sort("created_at")
    async for row in properties_docs:
        properties.append(Property(**row))
    return properties
