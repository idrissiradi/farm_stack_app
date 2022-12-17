import uuid
from typing import Optional
from datetime import datetime, timedelta

from pydantic import Field, BaseModel
from pydantic.json import timedelta_isoformat


class BaseClass(BaseModel):
    id: Optional[int] = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: Optional[datetime] = Field(alias="created_at", default=datetime.now())

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
            timedelta: timedelta_isoformat,
        }
