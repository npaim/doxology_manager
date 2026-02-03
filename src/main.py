from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.base import Base, engine
from src.db import models

from src.api.routes import songs

app = FastAPI(title="Doxology Manager API")

# create tables only for dev (alembic handles prod)
#Base.metadata.create_all(bind=engine)

app.include_router(songs.router, prefix="/songs", tags=["songs"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
