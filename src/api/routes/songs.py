from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth import get_current_leader
from src.db import crud
from src.db.base import SessionLocal
from src.db.models import Leader
from src.schemas import SongInsert, SongRead

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SongRead)
def create_song(song: SongInsert, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    return crud.insert_song(db, **song.model_dump())


@router.get("/", response_model=list[SongRead])
def list_songs(db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    return crud.get_all_songs(db)


@router.put("/{song_id}", response_model=SongRead)
def update_song(song_id: int, song: SongInsert, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    return crud.update_song(db, song_id, **song.model_dump())


@router.delete("/{song_id}", status_code=204)
def delete_song(song_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    crud.delete_song(db, song_id)
    return
