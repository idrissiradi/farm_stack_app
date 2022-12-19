from http import HTTPStatus
from typing import Any, Optional

from fastapi import Body, Path, Query, Depends, Request, APIRouter, HTTPException
from pydantic import EmailStr

from app.auth.models import UserModel
from app.core.security import get_current_user_authorizer
from app.core.services import create_aliased_response
from app.property.models import (
    Property,
    PropertyInCreate,
    PropertyInUpdate,
    PropertyInResponse,
    PropertyFilterParams,
    ManyPropertiesInResponse,
)
from app.property.services import (
    create_post,
    check_property_owner,
    delete_property_by_slug,
    update_property_by_slug,
)
from app.property.selectors import (
    get_properties,
    get_user_properties,
    get_property_by_slug,
)

router = APIRouter(prefix="/properties")


@router.get(
    "/feed",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
)
async def get_properties_feed(
    request: Request,
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    owner: str = "",
    type: str = "",
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
    "/all",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
)
async def get_properties_by_user(
    request: Request,
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
) -> Any:
    """Get user properties"""
    properties = await get_user_properties(request, user.username, limit, offset)
    return create_aliased_response(
        ManyPropertiesInResponse(
            properties=properties, properties_count=len(properties)
        )
    )


@router.post("/", response_model=PropertyInResponse, status_code=HTTPStatus.CREATED)
async def new_property(
    request: Request,
    post: PropertyInCreate = Body(..., embed=True),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Create new property"""
    if user:
        if not user.is_active and not user.is_verified:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="User not allowed"
            )
        new_post = create_post(request, post, user)
        if new_post:
            return create_aliased_response(new_post)
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get(
    "/{slug}",
    status_code=HTTPStatus.OK,
    response_model=PropertyInResponse,
)
async def get_property(
    request: Request,
    slug: str = Path(..., min_length=1),
) -> Any:
    """Get property by slug"""
    property: Property = await get_property_by_slug(request, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Property with slug '{slug}' not found",
        )
    return create_aliased_response(PropertyInResponse(property))


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
    await check_property_owner(request, slug, user.username)
    updated_property = await update_property_by_slug(request, slug, data)
    return create_aliased_response(PropertyInResponse(updated_property))


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
    await check_property_owner(request, slug, user.email)
    await delete_property_by_slug(request, slug, user.email)
    return {"message": "success"}
