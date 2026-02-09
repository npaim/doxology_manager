from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, date

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


@router.get("/services/new", response_class=HTMLResponse)
def new_service_form(
    request: Request,
    date: str,
):
    return templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service_date": date,
        },
    )


@router.post("/services/new")
def create_service(
    service_date: str = Form(...),
    preacher: str = Form(None),
    leader: str = Form(None),
    title:str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
):

    from src.db.models import Service
    from datetime import datetime

    service = Service(
        service_date=datetime.fromisoformat(service_date),
        preacher=preacher,
        leader=leader,
        title=title,
        notes=notes,
    )

    db.add(service)
    db.commit()

    return RedirectResponse("/", status_code=303)