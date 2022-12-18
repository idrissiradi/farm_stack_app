from http import HTTPStatus

from fastapi import Request, HTTPException
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def create_aliased_response(model: BaseModel) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(model, by_alias=True))
