import enum
from typing import Optional
from datetime import datetime

from pydantic import EmailStr, BaseModel, validator

from app.auth.utils import password_match, verify_password, get_password_hash
from app.core.model import BaseClass


class UserRole(str, enum.Enum):
    role_owner = "owner"
    role_staff = "staff"
    role_client = "client"


class AuthProvider(enum.Enum):
    auth_email = "email"
    auth_google = "google"


class UserBase(BaseClass):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr = None
    username: Optional[str] = None
    is_verified: Optional[bool] = False
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role: UserRole = UserRole.role_client
    auth_provider: AuthProvider = AuthProvider.auth_email


class UserInDB(UserBase):
    email: EmailStr
    password: str


class UserInLogin(BaseModel):
    email: EmailStr
    password: str


class UserInCreate(UserInLogin):
    first_name: str
    last_name: str
    password_confirm: str

    _check_password_confirm = validator("password_confirm", allow_reuse=True)(
        password_match
    )

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password)

    def change_password(self, password: str) -> str:
        self.password = get_password_hash(password)


class UserModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    role: UserRole


class UserInResponse(BaseModel):
    user: UserModel


class User(UserInResponse):
    token: str


class UserInUpdate(UserBase):
    password: Optional[str] = None


class UserTokenInDB(BaseClass):
    user_id: str
    token: str
    expired_at: Optional[datetime]


class ResetInDB(BaseClass):
    email: EmailStr
    token: str


class ResetSchema(BaseModel):
    password: str
    password_confirm: str
    token: str


class VerifyInDB(BaseClass):
    email: EmailStr
    token: str
