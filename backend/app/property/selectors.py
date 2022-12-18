from typing import List, Optional

from fastapi import Request

from app.property.models import Property


async def get_properties(
    request: Request, limit: int, offset: int
) -> Optional[List[Property]]:
    """Get feed properties"""

    properties: List[Property] = []
    properties_docs = request.app.mongodb.Properties.find(
        limit=limit, skip=offset
    ).sort("created_at")
    async for row in properties_docs:
        properties.append(Property(**row))
    return properties


async def get_property_by_slug(request: Request, slug: str) -> Property:
    """Get property by slug"""

    property = await request.app.mongodb.Properties.find_one({"slug": slug})
    return property
