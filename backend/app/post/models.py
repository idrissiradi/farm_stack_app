import enum
from typing import List, Optional

from pydantic import Field, AnyUrl, BaseModel

from app.core.model import BaseClass
from app.auth.models import UserModel


class PostType(str, enum.Enum):
    type_apartment = "Apartment"
    type_house = "House"
    type_villas = "Villas"
    type_office = "Office"
    type_Industrial = "Industrial"
    type_retail_space = "Retail Space"
    type_land = "Land"
    type_boat = "Boat"
    type_car = "Car"


class PostFilterParams(BaseModel):
    type: PostType = ""
    owner: str = ""
    limit: int = 20
    offset: int = 0


class PostBase(BaseClass):
    title: str
    slug: str
    description: str
    is_active: bool = True
    price: float
    post_type: Optional[PostType] = None


class Post(PostBase):
    owner: UserModel


class PostInDB(Post):
    pass


class PostInCreate(BaseModel):
    title: str
    description: str
    price: float
    post_type: PostType


class PostInResponse(BaseModel):
    post: Post


class ManyPostsInResponse(BaseModel):
    posts: List[Post]
    posts_count: int = Field(..., alias="postsCount")


class PostInUpdate(BaseModel):
    title: str
    slug: str
    description: str
    price: float
    post_type: Optional[PostType] = None


class Media(BaseClass):
    post_id: str
    is_feature: bool = False
    image_url: Optional[AnyUrl] = None


class MediaInUpdate(BaseModel):
    is_feature: bool
    image_url: Optional[AnyUrl]


class MediaInResponse(BaseModel):
    media: List[Media]
    media_count: int = Field(..., alias="mediaCount")
