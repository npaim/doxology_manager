from sqlalchemy.orm import Session
from src.db.models import Song


def insert_song(db: Session, title: str, hymn_number: int, misc: str | None = None):
    song = Song(title=title, hymn_number = hymn_number, misc = misc)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


def get_all_songs(db: Session):
    return db.query(Song).all()


def get_song_by_number(db: Session, hymn_number: int):
    return db.query(Song).filter(Song.hymn_number == hymn_number).first()