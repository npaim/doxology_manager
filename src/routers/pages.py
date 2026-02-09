from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime

from src.db.crud import get_services_for_month
from src.db.base import get_db

from sqlalchemy.orm import Session


templates = Jinja2Templates(directory="src/templates")

router = APIRouter()



import calendar
from collections import defaultdict

@router.get("/")
def calendar_view(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
):
    from datetime import datetime

    now = datetime.now()
    year = year or now.year
    month = month or now.month

    services = get_services_for_month(db, year, month)

    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(year, month)

    service_map = defaultdict(list)
    for s in services:
        service_map[s.service_date.date()].append(s)

    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "weeks": weeks,
            "service_map": service_map,
            "year": year,
            "month": month,
        },
    )
