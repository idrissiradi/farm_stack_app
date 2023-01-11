from datetime import datetime

from odmantic.bson import BSON_TYPES_ENCODERS, BaseBSONModel, ObjectId


class BaseModelClass(BaseBSONModel):
    id: ObjectId = ObjectId()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            **BSON_TYPES_ENCODERS,
            ObjectId: lambda oid: str(oid),
            datetime: lambda v: v.timestamp(),
        }
