from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
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
    created_at = Column(DateTime)
    created_by = Column(String, nullable=True)
    service_date = Column(DateTime)
    preacher = Column(String, nullable=True)
    responsible = Column(String, nullable=True)
