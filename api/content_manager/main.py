from contextlib import asynccontextmanager

from fastapi import FastAPI

from content_manager.db import engine
from content_manager.entities import Entity
from content_manager.exceptions import NotFoundException, handle_4xx_exception
from content_manager.routers import content


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(content.router)
app.add_exception_handler(NotFoundException, handle_4xx_exception)


@app.get("/healthcheck", tags=["Status"])
async def healthcheck():
    # TODO: Make a real healthcheck here.
    return {"status": "ok"}
