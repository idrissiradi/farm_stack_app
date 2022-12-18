from http import HTTPStatus
from typing import Any, Optional

from fastapi import Body, Path, Query, Depends, Request, APIRouter, HTTPException

from app.auth.models import UserModel
from app.core.security import get_current_user_authorizer
from app.core.services import is_authenticated, create_aliased_response
from app.property.models import (
    Property,
    PropertyInCreate,
    PropertyInUpdate,
    PropertyInResponse,
    ManyPropertiesInResponse,
)
from app.property.services import create_post
from app.property.selectors import get_properties, get_property_by_slug

router = APIRouter(prefix="/properties")


@router.post("/", response_model=PropertyInResponse, status_code=HTTPStatus.CREATED)
async def new_property(
    request: Request,
    post: PropertyInCreate = Body(..., embed=True),
    user: Optional[UserModel] = Depends(get_current_user_authorizer()),
) -> Any:
    """Create new property"""

    user = await is_authenticated(request)
    if user:
        if not user["is_active"] and not user["is_verified"]:
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
    user: Optional[UserModel] = Depends(get_current_user_authorizer(required=False)),
) -> Any:
    """Get property by slug"""

    property: Property = await get_property_by_slug(request, slug)
    if not property:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Property with slug '{slug}' not found",
        )

    return create_aliased_response(PropertyInResponse(property))


@router.get(
    "/feed",
    response_model=ManyPropertiesInResponse,
    status_code=HTTPStatus.OK,
)
async def get_properties_feed(
    request: Request,
    user: Optional[UserModel] = Depends(get_current_user_authorizer(required=False)),
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
) -> Any:
    """Feed properties"""

    properties = await get_properties(request, limit, offset)
    return create_aliased_response(
        ManyPropertiesInResponse(
            Properties=properties, Properties_count=len(properties)
        )
    )
