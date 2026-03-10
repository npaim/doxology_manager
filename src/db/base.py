from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from src.config import DATABASE_URL

# Configure engine with a short connect timeout for Postgres and pre_ping
try:
    url = make_url(DATABASE_URL)
except Exception:
    url = None

connect_args = {}
if url and url.drivername.startswith("postgresql"):
    connect_args["connect_timeout"] = 3  # seconds

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

print(">>> FASTAPI CONNECTING TO:", engine.url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
