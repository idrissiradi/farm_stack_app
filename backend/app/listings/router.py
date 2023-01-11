from http import HTTPStatus
from typing import Any, Optional

from fastapi import Body, Depends, APIRouter, HTTPException, Query, Path
from odmantic import AIOEngine
from app.auth.models import UserBase
from app.listings.models import (
    Media,
    MediaModel,
    ManyPropertiesInResponse,
    Property,
    PropertyBase,
    PropertyFilterParams,
    PropertyInCreate,
    PropertyInResponse,
    PropertyType,
)

from app.core.security import get_current_user_authorizer
from app.core.services import get_db
from app.listings.selectors import (
    all_property_reservation,
    get_properties,
    get_property_by_slug,
)
from app.listings.services import check_user_permission, create_property

router = APIRouter(prefix="/feed")


@router.get(
    "/",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
)
async def get_properties_feed(
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    owner: str = "",
    type: PropertyType = "",
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Feed properties"""
    filters = PropertyFilterParams(type=type, owner=owner, limit=limit, offset=offset)
    properties = await get_properties(engine, filters)
    return ManyPropertiesInResponse(
        properties=properties, properties_count=len(properties)
    )


@router.post(
    "/",
    response_model=PropertyBase,
    status_code=HTTPStatus.CREATED,
)
async def new_property(
    engine: AIOEngine = Depends(get_db),
    property: PropertyInCreate = Body(..., embed=True),
    user: Optional[UserBase] = Depends(get_current_user_authorizer()),
) -> Any:
    """Create new property"""
    await check_user_permission(engine, user)
    new_property = await create_property(engine, property, user)
    if new_property:
        return new_property
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get(
    "/{slug}",
    status_code=HTTPStatus.OK,
    response_model=PropertyInResponse,
)
async def get_property(
    engine: AIOEngine = Depends(get_db),
    slug: str = Path(..., min_length=1),
    user: Optional[UserBase] = Depends(get_current_user_authorizer(required=False)),
) -> Any:
    """Get property by slug"""
    property = await get_property_by_slug(engine, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Property with slug '{slug}' not found",
        )
    reservations = await all_property_reservation(engine, slug)
    return PropertyInResponse(property=property, reservations=reservations)


# @router.put(
#     "/{slug}",
#     status_code=HTTPStatus.OK,
#     response_model=PropertyInResponse,
# )
# async def update_property(
#     request: Request,
#     data: PropertyInUpdate = Body(..., embed=True),
#     slug: str = Path(..., min_length=1),
#     user: Optional[UserModel] = Depends(get_current_user_authorizer()),
# ) -> Any:
#     """Update Property"""
#     await check_user_permission(request, user, slug)
#     await check_property_owner(request, slug, user.email)
#     updated_property = await update_property_by_slug(request, slug, data)
#     return create_aliased_response(PropertyInResponse(property=updated_property))


# @router.delete(
#     "/{slug}",
#     status_code=HTTPStatus.NO_CONTENT,
# )
# async def delete_property(
#     request: Request,
#     slug: str = Path(..., min_length=1),
#     user: Optional[UserModel] = Depends(get_current_user_authorizer()),
# ) -> Any:
#     """Update Property"""
#     await check_user_permission(request, user, slug)
#     await check_property_owner(request, slug, user.email)
#     await delete_reservation_by_property_slug(
#         request,
#         slug,
#     )
#     await delete_property_by_slug(
#         request,
#         slug,
#         user.email,
#     )
#     return {"message": "success"}
