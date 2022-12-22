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
    type: str = ""
    owner: str = ""
    limit: int = 20
    offset: int = 0


class Address(BaseModel):
    street: str
    city: str


class Media(BaseClass):
    is_feature: bool = False
    image_url: Optional[AnyUrl] = None


class MediaModel(BaseModel):
    is_feature: bool
    image_url: Optional[AnyUrl]


class PropertyBase(BaseClass):
    title: str
    slug: str
    description: str
    is_active: bool = True
    price: float
    property_type: Optional[PropertyType] = None
    address: Address
    media: List[Media] = []


class Property(PropertyBase):
    owner: UserModel


class PropertyInDB(Property):
    pass


class PropertyInCreate(BaseModel):
    title: str
    description: str
    price: float
    property_type: PropertyType
    address: Address
    media: List[MediaModel]


class PropertyInResponse(BaseModel):
    property: Property


class ManyPropertiesInResponse(BaseModel):
    properties: List[Property]
    properties_count: int = Field(..., alias="properties_count")


class PropertyInUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = True
    property_type: Optional[PropertyType] = None
    address: Optional[Address] = None
    media: List[MediaModel] = None
