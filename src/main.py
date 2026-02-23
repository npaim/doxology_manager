from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.db.base import Base, engine
from src.db import models
from src.routers import pages

from src.api.routes import songs
from src.api.routes import services

app = FastAPI(title="Doxology Manager API")

# create tables only for dev (alembic handles prod)
#Base.metadata.create_all(bind=engine)

app.include_router(songs.router, prefix="/songs", tags=["songs"])
app.include_router(pages.router)
app.include_router(services.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
