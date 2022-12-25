from http import HTTPStatus
from typing import Any, Optional

from fastapi import Body, Path, Query, Depends, Request, APIRouter, HTTPException

from app.auth.models import UserModel
from app.admin.models import (
    Reservation,
    PropertyType,
    PropertyInCreate,
    PropertyInUpdate,
    ReservationModel,
    PropertyInResponse,
    ReservationInUpdate,
    PropertyFilterParams,
    ManyPropertiesInResponse,
    ManyReservationInResponse,
)
from app.core.security import get_current_user_authorizer
from app.core.services import create_aliased_response
from app.admin.services import (
    create_property,
    create_reservation,
    check_property_owner,
    check_user_permission,
    delete_property_by_slug,
    update_property_by_slug,
    update_owner_reservation,
)
from app.admin.selectors import (
    get_properties,
    get_user_properties,
    get_property_by_slug,
    all_property_reservation,
)

router = APIRouter(prefix="/properties")


@router.get(
    "/feed",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
    tags=["Properties"],
)
async def get_properties_feed(
    request: Request,
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    owner: str = "",
    type: PropertyType = "",
) -> Any:
    """Feed properties"""
    filters = PropertyFilterParams(type=type, owner=owner, limit=limit, offset=offset)
    properties = await get_properties(request, filters)
    return create_aliased_response(
        ManyPropertiesInResponse(
            properties=properties, properties_count=len(properties)
        )
    )


@router.get(
    "/feed/{slug}",
    status_code=HTTPStatus.OK,
    response_model=PropertyInResponse,
    tags=["Properties"],
)
async def get_property(
    request: Request,
    slug: str = Path(..., min_length=1),
    user: Optional[UserModel] = Depends(get_current_user_authorizer(required=False)),
) -> Any:
    """Get property by slug"""
    property = await get_property_by_slug(request, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Property with slug '{slug}' not found",
        )
    reservations = await all_property_reservation(request, slug)
    return create_aliased_response(
        PropertyInResponse(property=property, reservations=reservations)
    )


@router.get(
    "/",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
)
async def get_properties_by_user(
    request: Request,
    user: UserModel = Depends(get_current_user_authorizer()),
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    type: PropertyType = "",
) -> Any:
    """Get user properties"""
    await check_user_permission(request, user)
    filters = PropertyFilterParams(
        type=type, owner=user.username, limit=limit, offset=offset
    )
    properties = await get_user_properties(request, filters)
    return create_aliased_response(
        ManyPropertiesInResponse(
            properties=properties, properties_count=len(properties)
        )
    )


@router.post(
    "/",
    response_model=PropertyInResponse,
    status_code=HTTPStatus.CREATED,
)
async def new_property(
    request: Request,
    property: PropertyInCreate = Body(..., embed=True),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Create new property"""
    await check_user_permission(request, user)
    new_property = await create_property(request, property, user)
    if new_property:
        return create_aliased_response(new_property)
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get(
    "/{slug}",
    status_code=HTTPStatus.OK,
    response_model=PropertyInResponse,
)
async def get_user_property(
    request: Request,
    slug: str = Path(..., min_length=1),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Get user property by slug"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    reservations = await all_property_reservation(request, slug)
    property = await get_property_by_slug(request, slug)
    return create_aliased_response(
        PropertyInResponse(property=property, reservations=reservations)
    )


@router.put(
    "/{slug}",
    status_code=HTTPStatus.OK,
    response_model=PropertyInResponse,
)
async def update_property(
    request: Request,
    data: PropertyInUpdate = Body(..., embed=True),
    slug: str = Path(..., min_length=1),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Update Property"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    updated_property = await update_property_by_slug(request, slug, data)
    return create_aliased_response(PropertyInResponse(property=updated_property))


@router.delete(
    "/{slug}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_property(
    request: Request,
    slug: str = Path(..., min_length=1),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Update Property"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    await delete_property_by_slug(request, slug, user.email)
    return {"message": "success"}


@router.post(
    "/{slug}/reservations",
    response_model=ReservationModel,
    status_code=HTTPStatus.CREATED,
)
async def new_reservation(
    request: Request,
    slug: str = Path(..., min_length=1),
    reservation: ReservationModel = Body(..., embed=True),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
):
    """Create new reservation"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    new_reservation = await create_reservation(request, reservation, slug)
    if new_reservation:
        return create_aliased_response(ReservationModel(**new_reservation))
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get(
    "/{slug}/reservations",
    response_model=ReservationModel,
    status_code=HTTPStatus.CREATED,
)
async def get_all_reservations(
    request: Request,
    slug: str = Path(..., min_length=1),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
):
    """Get all reservations for existing property"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    reservations = await all_property_reservation(request, slug)
    return create_aliased_response(
        ManyReservationInResponse(
            reservations=reservations, reservations_count=len(reservations)
        )
    )


@router.put(
    "/{slug}/reservations",
    response_model=ReservationModel,
    status_code=HTTPStatus.CREATED,
)
async def update_reservation(
    request: Request,
    slug: str = Path(..., min_length=1),
    reservation: ReservationInUpdate = Body(..., embed=True),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
):
    """Create new reservation"""
    await check_user_permission(request, user, slug)
    await check_property_owner(request, slug, user.email)
    new_reservation = await update_owner_reservation(request, reservation)
    if new_reservation:
        return create_aliased_response(ReservationModel(**new_reservation))
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )
