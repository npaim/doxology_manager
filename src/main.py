from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.api.routes import services
from src.api.routes import songs
from src.config import SESSION_SECRET
from src.db import models
from src.routers import aliases
from src.routers import health
from src.routers import pages


app = FastAPI(title="Doxology Manager API")

app.include_router(songs.router, prefix="/songs", tags=["songs"])
app.include_router(aliases.router)
app.include_router(pages.router)
app.include_router(health.router)
app.include_router(services.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
