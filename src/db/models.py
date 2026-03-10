from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, Time, Boolean
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
    # legacy single time; kept for compatibility
    service_time = Column(Time, nullable=False)
    # new fields
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    preacher = Column(String, nullable=True)
    leader = Column(String, nullable=True)
    title = Column(String, nullable=True)
    songs = relationship(
        "ServiceSong",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceSong.position",
    )
    # ordered schedule/moments
    moments = relationship(
        "ServiceMoment",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceMoment.position",
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


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, nullable=False, server_default='1')


class ServiceMoment(Base):
    __tablename__ = "service_moments"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    responsible = Column(String, nullable=True)
    time = Column(Time, nullable=True)
    notes = Column(String, nullable=True)

    # optional link to a member
    responsible_member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)

    service = relationship("Service", back_populates="moments")
    responsible_member = relationship("Member")
