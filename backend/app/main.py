import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.post.router import router as post_router

app = FastAPI(title=settings.PROJECT_NAME)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_db_client():
    print("connect to the database...")
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.database_name]
    print("Successfully connected to the database！")


@app.on_event("shutdown")
async def shutdown_db_client():
    print("close database connection...")
    app.mongodb_client.close()
    print("database connection closed！")


app.include_router(auth_router, prefix=settings.API_STR, tags=["Authentication"])
app.include_router(post_router, prefix=settings.API_STR, tags=["Posts"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
