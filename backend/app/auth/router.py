import random
import string
from http import HTTPStatus
from typing import Any

# from rich import print  # dev mode
from fastapi import Body, Request, Response, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth.utils import get_password_hash
from app.auth.models import User, ResetSchema, UserInLogin, UserInCreate, UserInResponse
from app.auth.service import (
    create_user,
    authenticate,
    generate_token,
    send_verify_email,
    send_reset_password,
    generate_access_token,
)
from app.core.security import decode_access_token
from app.auth.selectors import (
    get_user_by_id,
    get_user_reset,
    get_user_token,
    get_verify_email,
    get_user_by_email,
)

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


@router.get("/verify", status_code=HTTPStatus.SEE_OTHER)
async def verify(request: Request, token: str, redirect_url: str) -> Any:
    """Verify user email"""

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
        {"email": user["email"]}, {"$set": {"is_verified": True}}
    )
    await request.app.mongodb.UserVerify.delete_one({"_id": verify_email["_id"]})
    return RedirectResponse(redirect_url)


@router.post("/login", response_model=User, status_code=HTTPStatus.OK)
async def login(data: UserInLogin, response: Response, request: Request) -> Any:
    """Login user, token login, get an access token"""

    user = await authenticate(request, email=data.email, password=data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect email or password"
        )
    elif not user["is_active"]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Inactive user")

    token = await generate_token(user["_id"], request, response)
    return User(user=user, token=token)


@router.post("/refresh", status_code=HTTPStatus.OK)
async def refresh_token(
    request: Request,
    response: Response,
) -> Any:
    """Refresh token API"""

    token = await generate_access_token(request, response)
    return token


@router.post("/logout", status_code=HTTPStatus.OK)
async def logout(request: Request, response: Response) -> Any:
    """Log out authenticated user"""

    refresh_token = request.cookies.get("refresh_token")
    token = await get_user_token(refresh_token)
    if not token:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Invalide credentials")

    await request.app.mongodb.UserToken.delete_one({"_id": token["_id"]})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "success"}


@router.post("/recover_password", status_code=HTTPStatus.OK)
async def recover_password(
    request: Request, email: str, background_tasks: BackgroundTasks
) -> Any:
    """Forget password"""

    user = await get_user_by_email(email=email, request=request)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user with this username does not exist in the system.",
        )
    await send_reset_password(user["email"], background_tasks, request)
    return {"message": "Password recovery email sent"}


@router.post("/reset", status_code=HTTPStatus.OK)
async def reset_password(request: Request, data: ResetSchema) -> Any:
    """Reset password"""

    if data.password != data.password_confirm:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Password do not match")

    user_reset = await get_user_reset(request, data.token)
    if not user_reset:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Invalid Link")

    user = await get_user_by_email(request, user_reset["email"])
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )

    hashed_password = get_password_hash(data.password)
    await request.app.mongodb.Users.update_one(
        {"_id": user["_id"]}, {"$set": {"password": hashed_password}}
    )
    await request.app.mongodb.UserReset.delete_one({"token": data.token})

    return {"message": "Password updated successfully"}


@router.get("/profile", status_code=HTTPStatus.OK, response_model=UserInResponse)
async def get_user(request: Request) -> Any:
    """Get current user"""

    access_token = request.cookies.get("access_token")
    if access_token:
        user_id = decode_access_token(access_token)
        user = await get_user_by_id(request, user_id)
        return UserInResponse(user=user)

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="The user with this username does not exist in the system.",
    )
