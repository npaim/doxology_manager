from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, date, time

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
    year: int = date.today().year,
    month: int = date.today().month,
    db: Session = Depends(get_db)
):

    cal = calendar.Calendar(firstweekday=6)

    month_days = cal.monthdatescalendar(year, month)

    services = get_services_for_month(db, year, month)

    services_by_date = {}

    for service in services:

        services_by_date.setdefault(
            service.service_date.date(),
            []
        ).append(service)


    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "calendar": month_days,
            "services_by_date": services_by_date,
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],

            "prev_month": month-1 if month>1 else 12,
            "prev_year": year if month>1 else year-1,

            "next_month": month+1 if month<12 else 1,
            "next_year": year if month<12 else year+1
        }
    )


@router.get("/services/new", response_class=HTMLResponse)
def new_service_form(
    request: Request,
    date: str | None = None
):
    return templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service_date": date,
            "service_time": ""
        },
    )


@router.post("/services/new")
def save_service(
    service_id: int = Form(None),
    service_date: str = Form(...),
    service_time: str = Form(...),
    preacher: str = Form(None),
    leader: str = Form(None),
    title: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
):

    from src.db.models import Service
    from datetime import datetime

    if service_id:

        service = db.query(Service).get(service_id)

        service.service_date = datetime.strptime(service_date,"%Y-%m-%d")

        service.service_time = datetime.strptime(
            service_time,"%H:%M"
        ).time()

        service.preacher = preacher
        service.leader = leader
        service.title = title
        service.notes = notes

    else:

        service = Service(

            service_date=datetime.strptime(service_date,"%Y-%m-%d"),

            service_time=datetime.strptime(
                service_time,"%H:%M"
            ).time(),

            preacher=preacher,
            leader=leader,
            title=title,
            notes=notes,
        )

        db.add(service)

    db.commit()

    return RedirectResponse("/", status_code=303)

@router.get("/services/{service_id}", response_class=HTMLResponse)
def service_detail(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    from src.db.models import Service

    service = db.query(Service).get(service_id)

    return templates.TemplateResponse(
        "service_detail.html",
        {
            "request": request,
            "service": service
        }
    )

@router.get("/services/{service_id}/edit", response_class=HTMLResponse)
def edit_service_form(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    from src.db.models import Service

    service = db.query(Service).get(service_id)

    return templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service": service
        },
    )