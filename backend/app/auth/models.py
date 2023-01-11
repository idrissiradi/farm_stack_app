import enum
from typing import Optional
from datetime import datetime

from odmantic import Field, Model, EmbeddedModel, ObjectId
from pydantic import EmailStr, BaseModel, validator

from app.auth.utils import password_match, verify_password, get_password_hash
from app.core.model import BaseModelClass


class UserRole(str, enum.Enum):
    role_buyer = "buyer"
    role_seller = "seller"
    role_staff = "staff"
    role_agent = "agent"


class AuthProvider(str, enum.Enum):
    auth_email = "email"
    auth_google = "google"


class User(Model, BaseModelClass):
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True)
    username: str = Field(unique=True)
    is_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = UserRole.role_buyer
    auth_provider: AuthProvider = AuthProvider.auth_email
    avatar: str = ""
    password: str

    class Config:
        collection = "users"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = UserRole.role_buyer
    auth_provider: AuthProvider = AuthProvider.auth_email
    avatar: str = ""


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


class UserInResponse(BaseModel):
    user: UserBase


class UserInLoginResponse(UserInResponse):
    token: str


class UserInUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None


class UserTokenInDB(Model):
    user_id: str = Field(unique=True)
    token: str = Field(unique=True)
    expired_at: datetime

    class Config:
        collection = "user_token"


class ResetInDB(Model):
    email: EmailStr = Field(unique=True)
    token: str = Field(unique=True)

    class Config:
        collection = "reset_password"


class ResetSchema(BaseModel):
    password: str
    password_confirm: str
    token: str


class VerifyInDB(Model):
    email: EmailStr = Field(unique=True)
    token: str = Field(unique=True)

    class Config:
        collection = "user_verify"
