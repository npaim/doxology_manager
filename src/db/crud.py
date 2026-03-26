from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.db.models import Service, ServiceSong, Song


def insert_song(db: Session, title: str, hymn_number: int, misc: str | None = None):
    title = title.upper()
    existing = db.query(Song).filter(or_(Song.title == title, Song.hymn_number == hymn_number)).first()
    if existing:
        if existing.title == title:
            raise HTTPException(status_code=409, detail="Este titulo ja existe!")
        if existing.hymn_number == hymn_number:
            raise HTTPException(status_code=409, detail="Musica com esse numero ja existe!")

    song = Song(title=title, hymn_number=hymn_number, misc=misc)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


def get_all_songs(db: Session):
    return db.query(Song).order_by(Song.title).all()


def get_song_by_number(db: Session, hymn_number: int):
    return db.query(Song).filter(Song.hymn_number == hymn_number).first()


def get_services_for_month(db: Session, church_id: int, year: int, month: int):
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return (
        db.query(Service)
        .filter(Service.church_id == church_id)
        .filter(Service.service_date >= start)
        .filter(Service.service_date < end)
        .order_by(Service.service_date)
        .all()
    )


def add_song_to_service(db: Session, service_id: int, song_id: int, position: int):
    ss = ServiceSong(service_id=service_id, song_id=song_id, position=position)
    db.add(ss)
    db.commit()


def update_song(db: Session, song_id: int, title: str, hymn_number: int, misc: str | None = None):
    title = title.upper()
    existing = (
        db.query(Song)
        .filter(or_(Song.title == title, Song.hymn_number == hymn_number))
        .filter(Song.id != song_id)
        .first()
    )
    if existing:
        if existing.title == title:
            raise HTTPException(status_code=409, detail="Este titulo ja existe!")
        if existing.hymn_number == hymn_number:
            raise HTTPException(status_code=409, detail="Musica com esse numero ja existe!")

    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    song.title = title
    song.hymn_number = hymn_number
    song.misc = misc
    db.commit()
    db.refresh(song)
    return song


def delete_song(db: Session, song_id: int):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
