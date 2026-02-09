from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    hymn_number = Column(Integer)
    misc = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("title"),
        UniqueConstraint("hymn_number"),
    )


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    created_by = Column(String, nullable=True)
    service_date = Column(DateTime, index=True, nullable=False)
    preacher = Column(String, nullable=True)
    leader = Column(String, nullable=True)
    title = Column(String, nullable=True)
    songs = relationship(
        "ServiceSong",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceSong.position",
    )
    notes = Column(String, nullable=True)


class ServiceSong(Base):
    __tablename__ = "service_songs"

    id = Column(Integer, primary_key=True)

    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )

    song_id = Column(
        Integer,
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False,
    )

    position = Column(Integer, nullable=False)

    service = relationship("Service", back_populates="songs")
    song = relationship("Song")

    __table_args__ = (
    UniqueConstraint("service_id", "song_id"),
    )
