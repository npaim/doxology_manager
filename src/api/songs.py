from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.base import SessionLocal
from src.db import crud
from src.schemas import SongInsert, SongRead


router = APIRouter(prefix="/songs", tags=["songs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

