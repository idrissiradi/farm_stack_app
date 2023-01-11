from typing import List, Optional


from app.auth.models import UserBase
from app.listings.models import (
    Property,
    PropertyBase,
    Reservation,
    ReservationModel,
    PropertyFilterParams,
)
from odmantic import AIOEngine, query


async def get_properties(
    engine: AIOEngine, filters: PropertyFilterParams
) -> Optional[List[PropertyBase]]:
    """Get feed properties"""

    base_query = {}
    if filters.owner:
        base_query["owner.username"] = filters.owner
    if filters.type:
        base_query["property_type"] = filters.type
    properties = await engine.find(
        Property,
        base_query,
        limit=filters.limit,
        skip=filters.offset,
        # sort=query.asc(Property.created_at),
    )
    return properties


async def get_property_by_slug(engine: AIOEngine, slug: str) -> Optional[Property]:
    """Get property by slug"""
    property = await engine.find_one(Property, Property.slug == slug)
    return property


async def all_property_reservation(
    engine: AIOEngine, slug: str
) -> Optional[List[Reservation]]:
    """Get all reservation for existing property"""
    property = await get_property_by_slug(engine, slug)
    reservations = engine.find(Reservation, Reservation.property_id == property.id)
    return reservations
