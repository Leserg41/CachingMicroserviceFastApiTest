from contextlib import asynccontextmanager
from fastapi import FastAPI

from .routers.payloads import router as payloads_router

from .database import Base, engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(payloads_router)