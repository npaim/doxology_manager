from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

print(">>> FASTAPI CONNECTING TO:", engine.url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
