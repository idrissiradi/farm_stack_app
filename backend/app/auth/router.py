from http import HTTPStatus
from typing import Any, Optional

from fastapi import (
    Body,
    Depends,
    Request,
    Response,
    APIRouter,
    HTTPException,
    BackgroundTasks,
)
from odmantic import AIOEngine
from fastapi.responses import RedirectResponse

from app.auth.utils import get_password_hash
from app.auth.models import (
    UserBase,
    ResetInDB,
    ResetSchema,
    UserInLogin,
    UserInCreate,
    UserInResponse,
    UserInLoginResponse,
    UserInUpdate,
)
from app.auth.services import (
    create_user,
    authenticate,
    generate_token,
    send_verify_email,
    send_reset_password,
    generate_access_token,
    update_user_profile,
)
from app.core.security import get_current_user_authorizer
from app.core.services import get_db
from app.auth.selectors import get_user_reset, get_verify_email, get_user_by_email

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserInResponse,
    status_code=HTTPStatus.CREATED,
)
async def register(
    background_tasks: BackgroundTasks,
    user: UserInCreate = Body(..., embed=True),
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Register new user"""
    check_user = await get_user_by_email(engine, user.email)
    if check_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Email already register"
        )

    new_user = await create_user(engine, user)
    if new_user:
        await send_verify_email(new_user.email, engine, background_tasks)
        return UserInResponse(user=new_user)
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST, detail="Something went wrong / Bad request"
    )


@router.get("/verify", status_code=HTTPStatus.SEE_OTHER)
async def verify(
    token: str, redirect_url: str, engine: AIOEngine = Depends(get_db)
) -> Any:
    """Verify user email by token"""
    verify_email = await get_verify_email(engine, token)
    if not verify_email:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid Link",
        )

    user = await get_user_by_email(engine, verify_email.email)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user with this email does not exist in the system.",
        )
    user.is_verified = True
    async with engine.session() as session:
        await session.save(user)
        await session.delete(verify_email)
    return RedirectResponse(redirect_url)


@router.post("/login", response_model=UserInLoginResponse, status_code=HTTPStatus.OK)
async def login(
    data: UserInLogin,
    response: Response,
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Login user, get an access/refresh token"""
    user = await authenticate(engine, email=data.email, password=data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Inactive user")
    token = await generate_token(engine, user.id, response)
    return UserInLoginResponse(user=user, token=token)


@router.post("/refresh", status_code=HTTPStatus.OK)
async def refresh_token(
    request: Request,
    response: Response,
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Refresh token API, Generate New Access Token"""
    refresh_token = request.cookies.get("refresh_token")
    token = await generate_access_token(engine, refresh_token, response)
    return token


@router.post("/logout", status_code=HTTPStatus.OK)
async def logout(response: Response) -> Any:
    """Log out authenticated user, Remove cookies"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "success"}


@router.post("/recover_password", status_code=HTTPStatus.OK)
async def recover_password(
    email: str,
    background_tasks: BackgroundTasks,
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Forget password"""
    user = await get_user_by_email(engine, email)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user with this username does not exist in the system.",
        )
    await send_reset_password(engine, user.email, background_tasks)
    return {"message": "Password recovery email sent"}


@router.put("/reset", status_code=HTTPStatus.OK)
async def reset_password(
    data: ResetSchema,
    engine: AIOEngine = Depends(get_db),
) -> Any:
    """Reset password"""
    if data.password != data.password_confirm:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Password do not match")

    user_reset = await get_user_reset(engine, data.token)
    if not user_reset:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Invalid Link")

    user = await get_user_by_email(engine, user_reset.email)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )

    hashed_password = get_password_hash(data.password)
    user.password = hashed_password
    async with engine.session() as session:
        await session.save(user)
        await session.delete(ResetInDB, ResetInDB.token == data.token)
    return {"message": "Password updated successfully"}


@router.get("/profile", status_code=HTTPStatus.OK, response_model=UserInResponse)
async def get_profile(
    user: Optional[UserBase] = Depends(get_current_user_authorizer()),
) -> Any:
    """Get current user Profile"""
    return UserInResponse(user=user)


@router.put("/profile", status_code=HTTPStatus.OK, response_model=UserInResponse)
async def update_profile(
    engine: AIOEngine = Depends(get_db),
    user: Optional[UserBase] = Depends(get_current_user_authorizer()),
    data: UserInUpdate = Body(..., embed=True),
) -> Any:
    """Update current user Profile"""
    new_user = await update_user_profile(engine, data, user)
    return UserInResponse(user=new_user)
