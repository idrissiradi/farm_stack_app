from odmantic import AIOEngine
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


async def get_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    engine = AIOEngine(client=client, database=settings.database_name)
    return engine


def create_aliased_response(model: BaseModel) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(model, by_alias=True))
