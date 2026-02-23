from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import Service

router = APIRouter()

@router.get("/api/services")
def api_services(db: Session = Depends(get_db)):

    services = db.query(Service).all()

    result = []

    for s in services:

        result.append({

            "id": s.id,

            "title": s.preacher,

            "start": s.service_date.strftime("%Y-%m-%d"),

            "extendedProps": {

                "time": s.service_time.strftime("%H:%M"),

                "preacher": s.preacher,

                "leader": s.leader,

                "title": s.title,

                "notes": s.notes

            }

        })

    return result