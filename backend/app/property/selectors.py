from typing import List, Optional

from fastapi import Request

from app.property.models import Property, PropertyFilterParams


async def get_properties(
    request: Request, filters: PropertyFilterParams
) -> Optional[List[Property]]:
    """Get feed properties"""
    properties: List[Property] = []
    base_query = {}
    if filters.owner:
        base_query["owner.username"] = filters.owner
    if filters.type:
        base_query["property_type"] = filters.type

    properties_docs = (
        request.app.mongodb.Properties.find(
            base_query,
        )
        .sort("created_at", -1)
        .skip(filters.offset)
        .limit(filters.limit)
    )
    async for row in properties_docs:
        properties.append(Property(**row))
    return properties


async def get_property_by_slug(request: Request, slug: str) -> Optional[Property]:
    """Get property by slug"""
    property = await request.app.mongodb.Properties.find_one({"slug": slug})
    if property:
        return Property(**property)
    return None


async def get_user_properties(
    request: Request, filters: PropertyFilterParams
) -> Optional[List[Property]]:
    """Get user properties"""
    properties: List[Property] = []
    base_query = {}
    base_query["owner.username"] = filters.owner
    if filters.type:
        base_query["property_type"] = filters.type
    properties_docs = (
        request.app.mongodb.Properties.find(
            base_query,
        )
        .sort("created_at", -1)
        .skip(filters.offset)
        .limit(filters.limit)
    )
    async for row in properties_docs:
        properties.append(Property(**row))
    return properties
