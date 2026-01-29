from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.base import SessionLocal
from src.db import crud
from src.schemas import SongInsert, SongRead