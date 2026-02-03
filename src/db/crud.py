from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from src.db.models import Song


def insert_song(
    db: Session,
    title: str,
    hymn_number: int,
    misc: str | None = None,
):

    # Normalize title
    title = title.upper()

    # Check duplicates
    existing = (
        db.query(Song)
        .filter(
            or_(
                Song.title == title,
                Song.hymn_number == hymn_number,
            )
        )
        .first()
    )

    if existing:
        if existing.title == title:
            raise HTTPException(
                status_code=409,
                detail="Este título já existe!",
            )

        if existing.hymn_number == hymn_number:
            raise HTTPException(
                status_code=409,
                detail="Música com esse número já existe!",
            )

    # Insert
    song = Song(
        title=title,
        hymn_number=hymn_number,
        misc=misc,
    )

    db.add(song)
    db.commit()
    db.refresh(song)

    return song


def get_all_songs(db: Session):
    return db.query(Song).all()


def get_song_by_number(db: Session, hymn_number: int):
    return db.query(Song).filter(Song.hymn_number == hymn_number).first()
