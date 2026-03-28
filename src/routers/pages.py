import calendar
from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth import get_optional_leader, hash_password, login_leader, logout_leader, verify_password
from src.db.base import get_db
from src.db.crud import get_services_for_month
from src.db.models import Church, Leader, Member, Moment, Service, ServiceMoment, Template

templates = Jinja2Templates(directory="src/templates")
router = APIRouter()


def ensure_member(db: Session, name: str | None):
    if not name:
        return
    name = name.strip()
    if not name:
        return
    existing = db.query(Member).filter(func.lower(Member.name) == func.lower(name)).first()
    if not existing:
        db.add(Member(name=name))
        db.flush()


def setup_incomplete(db: Session) -> bool:
    return db.query(Leader).count() == 0


def require_page_leader(request: Request, db: Session) -> Leader | RedirectResponse:
    if setup_incomplete(db):
        return RedirectResponse("/setup", status_code=303)
    leader = get_optional_leader(request, db)
    if not leader:
        return RedirectResponse("/login", status_code=303)
    return leader


def require_admin_leader(request: Request, db: Session) -> Leader | RedirectResponse:
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    if leader.role != "admin":
        return RedirectResponse("/", status_code=303)
    return leader


def get_service_for_leader(db: Session, church_id: int, service_id: int) -> Service | None:
    return db.query(Service).filter(Service.id == service_id, Service.church_id == church_id).first()


def resolve_service_template(db: Session, service: Service) -> Template | None:
    if getattr(service, "template", None):
        return service.template
    if getattr(service, "template_id", None):
        return db.query(Template).filter(Template.id == service.template_id).first()

    template_ids = [
        tid for (tid,) in (
            db.query(Moment.template_id)
            .join(ServiceMoment, ServiceMoment.moment_id == Moment.id)
            .filter(ServiceMoment.service_id == service.id, Moment.template_id.isnot(None))
            .distinct()
            .all()
        ) if tid is not None
    ]
    if len(template_ids) == 1:
        return db.query(Template).filter(Template.id == template_ids[0]).first()
    return None


def get_template_moment_options(db: Session, template: Template | None):
    if not template:
        return [], []
    preset_moments = (
        db.query(Moment)
        .filter(Moment.template_id == template.id, Moment.is_active == True, Moment.default_moment == True)
        .order_by(Moment.position, Moment.name)
        .all()
    )
    is_livre = bool((template.name or "").strip().lower() == "livre")
    extra_moments_query = db.query(Moment).filter(Moment.is_active == True)
    if not is_livre:
        extra_moments_query = extra_moments_query.filter(Moment.template_id == template.id)
    extra_moments = extra_moments_query.order_by(Moment.position, Moment.name).all()
    return preset_moments, extra_moments


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request, db: Session = Depends(get_db)):
    if not setup_incomplete(db):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("setup.html", {"request": request})


@router.post("/setup")
def setup_submit(
    request: Request,
    church_name: str = Form(...),
    leader_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if not setup_incomplete(db):
        return RedirectResponse("/", status_code=303)

    church = db.query(Church).order_by(Church.id).first()
    if church and church.name == "Default Church":
        church.name = church_name.strip()
    else:
        church = Church(name=church_name.strip())
        db.add(church)
        db.flush()

    leader = Leader(
        church_id=church.id,
        name=leader_name.strip(),
        email=email.strip().lower(),
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(leader)
    db.commit()
    db.refresh(leader)
    login_leader(request, leader)
    return RedirectResponse("/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    if setup_incomplete(db):
        return RedirectResponse("/setup", status_code=303)
    leader = get_optional_leader(request, db)
    if leader:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if setup_incomplete(db):
        return RedirectResponse("/setup", status_code=303)

    leader = db.query(Leader).filter(func.lower(Leader.email) == func.lower(email.strip())).first()
    if not leader or not leader.is_active or not verify_password(password, leader.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."}, status_code=400)

    login_leader(request, leader)
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout_submit(request: Request):
    logout_leader(request)
    return RedirectResponse("/login", status_code=303)


@router.get("/")
def calendar_view(
    request: Request,
    year: int = date.today().year,
    month: int = date.today().month,
    db: Session = Depends(get_db),
):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)
    services = get_services_for_month(db, leader.church_id, year, month)
    services_by_date = {}
    for service in services:
        services_by_date.setdefault(service.service_date.date(), []).append(service)

    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "calendar": month_days,
            "services_by_date": services_by_date,
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],
            "prev_month": month - 1 if month > 1 else 12,
            "prev_year": year if month > 1 else year - 1,
            "next_month": month + 1 if month < 12 else 1,
            "next_year": year if month < 12 else year + 1,
        },
    )


@router.get("/admin/church", response_class=HTMLResponse)
def church_admin_page(request: Request, db: Session = Depends(get_db)):
    leader = require_admin_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    church = db.query(Church).get(leader.church_id)
    leaders = db.query(Leader).filter(Leader.church_id == leader.church_id).order_by(Leader.name).all()
    return templates.TemplateResponse("church_admin.html", {"request": request, "church": church, "leaders": leaders})


@router.post("/admin/church")
def update_church_submit(
    request: Request,
    church_name: str = Form(...),
    db: Session = Depends(get_db),
):
    leader = require_admin_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    church = db.query(Church).get(leader.church_id)
    church.name = church_name.strip()
    db.commit()
    login_leader(request, leader)
    return RedirectResponse("/admin/church", status_code=303)


@router.post("/admin/leaders/{leader_id}")
def update_leader_submit(
    leader_id: int,
    request: Request,
    role: str = Form(...),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db),
):
    admin = require_admin_leader(request, db)
    if isinstance(admin, RedirectResponse):
        return admin

    target = db.query(Leader).filter(Leader.id == leader_id, Leader.church_id == admin.church_id).first()
    if not target:
        return RedirectResponse("/admin/church", status_code=303)

    target.role = "admin" if role == "admin" else "leader"
    target.is_active = bool(is_active)
    db.commit()
    if target.id == admin.id:
        db.refresh(target)
        login_leader(request, target)
    return RedirectResponse("/admin/church", status_code=303)


@router.get("/leaders/new", response_class=HTMLResponse)
def new_leader_form(request: Request, db: Session = Depends(get_db)):
    leader = require_admin_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    return templates.TemplateResponse("leader_form.html", {"request": request})


@router.post("/leaders/new")
def create_leader_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("leader"),
    db: Session = Depends(get_db),
):
    leader = require_admin_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader

    existing = db.query(Leader).filter(func.lower(Leader.email) == func.lower(email.strip())).first()
    if existing:
        return templates.TemplateResponse("leader_form.html", {"request": request, "error": "Email already in use."}, status_code=400)

    db.add(
        Leader(
            church_id=leader.church_id,
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role="admin" if role == "admin" else "leader",
        )
    )
    db.commit()
    return RedirectResponse("/admin/church", status_code=303)


@router.get("/services/new", response_class=HTMLResponse)
def new_service_form(request: Request, date: str | None = None, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    selected_date = date or datetime.today().strftime("%Y-%m-%d")
    return templates.TemplateResponse("service_form.html", {"request": request, "service_date": selected_date, "start_time": "", "end_time": ""})


@router.post("/services/new")
async def save_service(
    request: Request,
    service_id: int = Form(None),
    selected_template_id: int | None = Form(None),
    service_date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    preacher: str = Form(None),
    leader: str = Form(None),
    title: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
):
    current_leader = require_page_leader(request, db)
    if isinstance(current_leader, RedirectResponse):
        return current_leader

    if service_id:
        service = get_service_for_leader(db, current_leader.church_id, service_id)
        if not service:
            return RedirectResponse("/", status_code=303)
        service.service_date = datetime.strptime(service_date, "%Y-%m-%d")
        service.start_time = datetime.strptime(start_time, "%H:%M").time()
        service.end_time = datetime.strptime(end_time, "%H:%M").time()
        service.service_time = service.start_time
        service.preacher = preacher
        service.leader = leader
        service.title = title
        service.notes = notes
        service.template_id = selected_template_id
        ensure_member(db, preacher)
        ensure_member(db, leader)
        db.commit()
        return RedirectResponse("/", status_code=303)

    try:
        sd = datetime.strptime(service_date, "%Y-%m-%d")
        st_start = datetime.strptime(start_time, "%H:%M").time()
        st_end = datetime.strptime(end_time, "%H:%M").time()
    except Exception:
        return templates.TemplateResponse("service_form.html", {"request": request, "service_date": service_date, "start_time": start_time, "end_time": end_time, "selected_template_id": selected_template_id, "error": "Please provide a valid date and time."}, status_code=400)

    if st_end < st_start:
        return templates.TemplateResponse("service_form.html", {"request": request, "service_date": service_date, "start_time": start_time, "end_time": end_time, "selected_template_id": selected_template_id, "error": "End time must be after start time."}, status_code=400)

    service = Service(
        church_id=current_leader.church_id,
        created_by=current_leader.email,
        service_date=sd,
        service_time=st_start,
        start_time=st_start,
        end_time=st_end,
        preacher=preacher,
        leader=leader,
        title=title,
        notes=notes,
        template_id=selected_template_id,
    )
    db.add(service)
    ensure_member(db, preacher)
    ensure_member(db, leader)
    db.commit()

    try:
      form = await request.form()
      mc = form.get("moments_count")
      if mc:
        total = int(mc)
        pos = 1
        for i in range(1, total + 1):
            moment_title = (form.get(f"moment_title_{i}") or "").strip()
            preset_moment_id = form.get(f"moment_id_{i}")
            rname = (form.get(f"moment_responsible_{i}") or "").strip()
            tval = form.get(f"moment_time_{i}")
            notes_val = (form.get(f"moment_notes_{i}") or "").strip()
            t = datetime.strptime(tval, "%H:%M").time() if tval else None
            responsible_member_id = None
            if rname:
                member = db.query(Member).filter(func.lower(Member.name) == func.lower(rname)).first()
                if not member:
                    member = Member(name=rname)
                    db.add(member)
                    db.flush()
                responsible_member_id = member.id
            if moment_title:
                db.add(ServiceMoment(service_id=service.id, position=pos, title=moment_title, responsible=rname or None, time=t, notes=notes_val or None, moment_id=int(preset_moment_id) if preset_moment_id else None, responsible_member_id=responsible_member_id))
                pos += 1
        db.commit()
    except Exception:
      pass

    return RedirectResponse("/", status_code=303)


@router.get("/services/{service_id}", response_class=HTMLResponse)
def service_detail(service_id: int, request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)
    service_template = resolve_service_template(db, service)
    return templates.TemplateResponse("service_detail.html", {"request": request, "service": service, "service_template": service_template})


@router.get("/services/{service_id}/edit", response_class=HTMLResponse)
def edit_service_form(service_id: int, request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)
    service_template = resolve_service_template(db, service)
    preset_moments, extra_moments = get_template_moment_options(db, service_template)
    return templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service": service,
            "selected_template_id": (service.template_id or (service_template.id if service_template else None)),
            "selected_template_name": (service_template.name if service_template else None),
            "preset_moments": preset_moments,
            "extra_moments": extra_moments,
        },
    )


@router.get("/songs", response_class=HTMLResponse)
def songs_page(request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    return templates.TemplateResponse("songs.html", {"request": request})


@router.get("/services/{service_id}/print", response_class=HTMLResponse)
def print_service(service_id: int, request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)
    moments = db.query(ServiceMoment).filter(ServiceMoment.service_id == service_id).order_by(ServiceMoment.position).all()
    return templates.TemplateResponse("service_print.html", {"request": request, "service": service, "moments": moments})


@router.get("/services/{service_id}/moments/new", response_class=HTMLResponse)
def new_moment_form(service_id: int, request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("moment_form.html", {"request": request, "service_id": service_id, "service_title": (service.title or "Service")})


@router.post("/services/{service_id}/moments/new", response_class=HTMLResponse)
def create_moment_submit(
    service_id: int,
    request: Request,
    title: str = Form(...),
    responsible: str = Form(None),
    time: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)

    max_pos = db.query(func.max(ServiceMoment.position)).filter(ServiceMoment.service_id == service_id).scalar() or 0
    responsible_member_id = None
    if responsible and responsible.strip():
        name = responsible.strip()
        member = db.query(Member).filter(func.lower(Member.name) == func.lower(name)).first()
        if not member:
            member = Member(name=name)
            db.add(member)
            db.flush()
        responsible_member_id = member.id

    db.add(ServiceMoment(service_id=service_id, position=int(max_pos) + 1, title=title, responsible=responsible.strip() if responsible else None, time=datetime.strptime(time, "%H:%M").time() if time else None, notes=notes or None, responsible_member_id=responsible_member_id))
    db.commit()
    return RedirectResponse(f"/services/{service_id}", status_code=303)


@router.get("/services/new/choose", response_class=HTMLResponse)
def choose_service_template(request: Request, date: str | None = None, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    templates_list = db.query(Template).order_by(Template.name).all()
    selected_date = date or datetime.today().strftime("%Y-%m-%d")
    return templates.TemplateResponse("service_template_select.html", {"request": request, "templates": templates_list, "date": selected_date})


@router.get("/services/new_with_template", response_class=HTMLResponse)
def new_service_with_template(request: Request, template_id: int, date: str | None = None, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader

    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return RedirectResponse("/services/new/choose", status_code=303)

    preset_moments, extra_moments = get_template_moment_options(db, template)
    selected_date = date or datetime.today().strftime("%Y-%m-%d")
    return templates.TemplateResponse("service_form.html", {"request": request, "service_date": selected_date, "start_time": "", "end_time": "", "preset_moments": preset_moments, "extra_moments": extra_moments, "selected_template_id": template_id, "selected_template_name": template.name})


@router.get("/services/{service_id}/moments/edit", response_class=HTMLResponse)
def edit_moments_page(service_id: int, request: Request, db: Session = Depends(get_db)):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader
    service = get_service_for_leader(db, leader.church_id, service_id)
    if not service:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("moments_edit.html", {"request": request, "service": service})
