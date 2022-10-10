import uuid
from http import HTTPStatus
from typing import Any

from rich import print  # dev mode
from fastapi import Body, Request, Response, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth.models import User, UserBase, UserInLogin, UserInCreate, UserInResponse
from app.auth.service import (
    create_user,
    authenticate,
    generate_token,
    send_verify_email,
)
from app.auth.selectors import get_user_token, get_verify_email, get_user_by_email

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
    """Verify user email"""

    verify_email = await get_verify_email(request, token)
    if not verify_email:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid Link",
        )

    user = await get_user_by_email(request, verify_email["email"])
    print(user["email"])
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user with this email does not exist in the system.",
        )

    await request.app.mongodb.Users.update_one(
        {"email": user["email"]}, {"$set": {"is_verified": True}}
    )
    await request.app.mongodb.UserVerify.delete_one({"_id": verify_email["_id"]})
    return redirect_url


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

    access_token = await generate_token(user["_id"], request, response)
    return User(user=user, token=access_token)


@router.post("/logout")
async def logout(request: Request, response: Response) -> Any:
    """Log out authenticated user"""

    refresh_token = request.cookies.get("refresh_token")
    token = await get_user_token(refresh_token)
    print("refresh token : ", refresh_token)
    print("token : ", token)
    print("token id : ", token["_id"])

    if not token:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Invalide credentials")

    await request.app.mongodb.UserToken.delete_one({"_id": token["_id"]})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "success"}
