import enum
from typing import List, Optional

from pydantic import Field, AnyUrl, BaseModel

from app.core.model import BaseClass
from app.auth.models import UserModel


class PropertyType(str, enum.Enum):
    type_apartment = "Apartment"
    type_house = "House"
    type_villas = "Villas"
    type_office = "Office"
    type_Industrial = "Industrial"
    type_retail_space = "Retail Space"
    type_land = "Land"
    type_boat = "Boat"
    type_car = "Car"


class PropertyFilterParams(BaseModel):
    type: PropertyType = ""
    owner: str = ""
    limit: int = 20
    offset: int = 0


class PropertyBase(BaseClass):
    title: str
    slug: str
    description: str
    is_active: bool = True
    price: float
    Property_type: Optional[PropertyType] = None


class Property(PropertyBase):
    owner: UserModel


class PropertyInDB(Property):
    pass


class PropertyInCreate(BaseModel):
    title: str
    description: str
    price: float
    Property_type: PropertyType


class PropertyInResponse(BaseModel):
    Property: Property


class ManyPropertiesInResponse(BaseModel):
    Properties: List[Property]
    Properties_count: int = Field(..., alias="Properties_count")


class PropertyInUpdate(BaseModel):
    title: str
    slug: str
    description: str
    price: float
    Property_type: Optional[PropertyType] = None


class Media(BaseClass):
    Property_id: str
    is_feature: bool = False
    image_url: Optional[AnyUrl] = None


class MediaInUpdate(BaseModel):
    is_feature: bool
    image_url: Optional[AnyUrl]


class MediaInResponse(BaseModel):
    media: List[Media]
    media_count: int = Field(..., alias="media_count")
