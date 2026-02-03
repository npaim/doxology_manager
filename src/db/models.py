from sqlalchemy import Column, Integer, String
from src.db.base import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    hymn_number = Column(Integer)
    misc = Column(String, nullable=True)