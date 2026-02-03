import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://doxology:doxology@localhost:5432/doxology_db",
)
