from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.base import SessionLocal
from src.db import crud
from src.schemas import SongInsert, SongRead

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SongRead)
def create_song(song: SongInsert, db: Session = Depends(get_db)):
    return crud.insert_song(db, **song.model_dump())


@router.get("/", response_model=list[SongRead])
def list_songs(db: Session = Depends(get_db)):
    return crud.get_all_songs(db)
