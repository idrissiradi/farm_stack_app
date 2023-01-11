import enum
from typing import List, Optional
from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field

from app.core.model import BaseModelClass
from app.auth.models import UserBase
from odmantic import Model, EmbeddedModel, ObjectId


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


class Address(EmbeddedModel):
    street: str
    city: str


class MediaModel(BaseModel):
    is_feature: bool
    image_url: Optional[AnyUrl]


class Media(Model, BaseModelClass, MediaModel):
    pass


class MediaInResponse(MediaModel):
    media_id: str


class ReservationModel(BaseModel):
    property_id: str
    body: str = ""
    date_start: datetime = datetime.now()
    date_end: datetime


class Reservation(Model, BaseModelClass, ReservationModel):
    pass


class ReservationInUpdate(BaseModel):
    date_start: Optional[datetime] = datetime.now()
    date_end: Optional[datetime]
    body: str = ""


class ReservationInResponse(ReservationModel):
    reservation_id: str


class ManyReservationInResponse(BaseModel):
    reservations: List[ReservationInResponse]
    reservations_count: int = Field(..., alias="reservations_count")


class PropertyBase(BaseModel):
    title: str
    slug: str
    description: str
    is_active: bool = True
    price: float
    property_type: PropertyType = PropertyType.type_house
    address: Address


class Property(Model, BaseModelClass):
    owner: UserBase
    title: str
    slug: str
    description: str
    is_active: bool = True
    price: float
    property_type: PropertyType = PropertyType.type_house
    address: Address


class PropertyInCreate(BaseModel):
    title: str
    description: str
    price: float
    property_type: PropertyType
    address: Address
    # media: List[MediaModel]


class PropertyInResponse(BaseModel):
    property: PropertyBase
    reservations: List[ReservationInResponse] = []


class ManyPropertiesInResponse(BaseModel):
    properties: List[PropertyBase]
    properties_count: int = Field(..., alias="properties_count")


class PropertyInUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = True
    property_type: Optional[PropertyType] = None
    address: Optional[Address] = None
    media: List[MediaModel] = None


# class StaffModel(BaseModel):
#     user_id: str
#     property_id: str


# class Staff(BaseClass, StaffModel):
#     pass
