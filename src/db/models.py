from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base import Base


class Church(Base):
    __tablename__ = "churches"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    leaders = relationship("Leader", back_populates="church", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="church")


class Leader(Base):
    __tablename__ = "leaders"

    id = Column(Integer, primary_key=True)
    church_id = Column(Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default="admin")
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    church = relationship("Church", back_populates="leaders")


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
    church_id = Column(Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    service_date = Column(DateTime, index=True, nullable=False)
    service_time = Column(Time, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    preacher = Column(String, nullable=True)
    leader = Column(String, nullable=True)
    title = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="SET NULL"), nullable=True, index=True)

    church = relationship("Church", back_populates="services")
    template = relationship("Template", back_populates="services")
    songs = relationship("ServiceSong", back_populates="service", cascade="all, delete-orphan", order_by="ServiceSong.position")
    moments = relationship("ServiceMoment", back_populates="service", cascade="all, delete-orphan", order_by="ServiceMoment.position")


class ServiceSong(Base):
    __tablename__ = "service_songs"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
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
    is_active = Column(Boolean, nullable=False, server_default="1")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    services = relationship("Service", back_populates="template")
    moments = relationship("Moment", back_populates="template")


class Moment(Base):
    __tablename__ = "moments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="RESTRICT"), nullable=True, index=True)
    default_moment = Column(Boolean, nullable=False, server_default="0")
    duration_min = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")

    template = relationship("Template", back_populates="moments")
    service_moments = relationship("ServiceMoment", back_populates="moment")


class ServiceMoment(Base):
    __tablename__ = "service_moments"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    responsible = Column(String, nullable=True)
    time = Column(Time, nullable=True)
    notes = Column(String, nullable=True)
    moment_id = Column(Integer, ForeignKey("moments.id", ondelete="RESTRICT"), nullable=True, index=True)
    responsible_member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)

    service = relationship("Service", back_populates="moments")
    responsible_member = relationship("Member")
    moment = relationship("Moment", back_populates="service_moments")
