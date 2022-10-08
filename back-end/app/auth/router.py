from http import HTTPStatus
from typing import Any

from rich import print  # dev mode
from fastapi import Body, Request, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth.models import UserInCreate, UserInResponse
from app.auth.service import create_user, send_verify_email
from app.auth.selectors import get_verify_email, get_user_by_email

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserInResponse,
    status_code=HTTPStatus.CREATED,
)
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    user: UserInCreate = Body(..., embed=True),
) -> Any:
    """Register new user API"""

    check_user = await get_user_by_email(request, user.email)
    if check_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Email already register"
        )

    new_user = await create_user(request, user)
    if new_user:
        email = new_user["email"]
        await send_verify_email(email, request, background_tasks)
        return JSONResponse(content=new_user)

    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get("/verify", response_class=RedirectResponse, status_code=HTTPStatus.OK)
async def verify(request: Request, token: str, redirect_url: str) -> Any:
    """Verify email"""

    verify_email = await get_verify_email(request, token)
    if not verify_email:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid Link",
        )

    user = await get_user_by_email(request, verify_email["email"])
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user with this email does not exist in the system.",
        )

    await request.app.mongodb.Users.update_one(
        {"_id": user["_id"]}, {"$set": {"is_verified": True}}
    )

    await request.app.mongodb.Verify.delete_one({"_id": verify_email["_id"]})

    return redirect_url
