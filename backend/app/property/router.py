from http import HTTPStatus
from typing import Any

from fastapi import Body, Query, Request, Response, APIRouter, HTTPException

from app.core.services import is_authenticated, create_aliased_response
from app.property.models import (
    PropertyInCreate,
    PropertyInUpdate,
    PropertyInResponse,
    ManyPropertiesInResponse,
)
from app.property.services import create_post
from app.property.selectors import get_properties

router = APIRouter(prefix="/properties")


@router.post("/", response_model=PropertyInResponse, status_code=HTTPStatus.CREATED)
async def new_property(
    request: Request, post: PropertyInCreate = Body(..., embed=True)
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


@router.get("/feed", response_model=ManyPropertiesInResponse, status_code=HTTPStatus.OK)
async def properties_feed(
    request: Request,
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
