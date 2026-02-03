from fastapi import FastAPI
from src.db.base import Base, engine
from src.db import models

from src.api.routes import songs

app = FastAPI(title="Doxology Manager API")

# create tables only for dev (alembic handles prod)
#Base.metadata.create_all(bind=engine)

app.include_router(songs.router, prefix="/songs", tags=["songs"])
