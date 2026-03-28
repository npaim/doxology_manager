import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth import get_current_leader
from src.db.base import get_db
from src.db.models import Leader, Member, Moment, Service, ServiceMoment, Template
from src.schemas import MemberCreate, MemberRead, MomentCreate, MomentRead, MomentUpdate, ServiceUpdate

router = APIRouter()


def get_service_or_404(db: Session, church_id: int, service_id: int) -> Service:
    service = db.query(Service).filter(Service.id == service_id, Service.church_id == church_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def resolve_service_template_name(db: Session, service: Service) -> str | None:
    if getattr(service, "template", None) and service.template.name:
        return service.template.name
    if getattr(service, "template_id", None):
        name = db.query(Template.name).filter(Template.id == service.template_id).scalar()
        if name:
            return name

    template_ids = [tid for (tid,) in (
        db.query(Moment.template_id)
        .join(ServiceMoment, ServiceMoment.moment_id == Moment.id)
        .filter(ServiceMoment.service_id == service.id, Moment.template_id.isnot(None))
        .distinct()
        .all()
    ) if tid is not None]
    if len(template_ids) == 1:
        return db.query(Template.name).filter(Template.id == template_ids[0]).scalar()
    return None


@router.get("/api/services")
def api_services(db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    services = db.query(Service).filter(Service.church_id == leader.church_id).order_by(Service.service_date).all()
    return [
        {
            "id": s.id,
            "title": s.preacher,
            "start": s.service_date.strftime("%Y-%m-%d"),
            "extendedProps": {
                "start_time": (s.start_time or s.service_time).strftime("%H:%M") if (s.start_time or s.service_time) else None,
                "end_time": (s.end_time or s.service_time).strftime("%H:%M") if (s.end_time or s.service_time) else None,
                "preacher": s.preacher,
                "leader": s.leader,
                "title": s.title,
                "notes": s.notes,
                "template_name": resolve_service_template_name(db, s),
            },
        }
        for s in services
    ]


@router.put("/api/services/{service_id}")
def update_service(service_id: int, payload: ServiceUpdate, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    s = get_service_or_404(db, leader.church_id, service_id)
    if payload.service_date is not None:
        s.service_date = datetime.strptime(payload.service_date, "%Y-%m-%d")
    if (payload.start_time is not None) or (payload.service_time is not None):
        st = payload.start_time or payload.service_time
        s.start_time = datetime.strptime(st, "%H:%M").time()
        s.service_time = s.start_time
    if payload.end_time is not None:
        s.end_time = datetime.strptime(payload.end_time, "%H:%M").time()
    if payload.preacher is not None:
        s.preacher = payload.preacher
    if payload.leader is not None:
        s.leader = payload.leader
    if payload.title is not None:
        s.title = payload.title
    if payload.notes is not None:
        s.notes = payload.notes
    db.commit()
    return {"ok": True}


@router.delete("/api/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    s = get_service_or_404(db, leader.church_id, service_id)
    db.delete(s)
    db.commit()
    return


@router.get("/api/services/{service_id}/moments", response_model=list[MomentRead])
def list_moments(service_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    get_service_or_404(db, leader.church_id, service_id)
    return db.query(ServiceMoment).filter(ServiceMoment.service_id == service_id).order_by(ServiceMoment.position).all()


@router.post("/api/services/{service_id}/moments", response_model=MomentRead)
def create_moment(service_id: int, payload: MomentCreate, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    get_service_or_404(db, leader.church_id, service_id)
    if payload.moment_id is not None:
        preset = db.query(Moment).filter(Moment.id == payload.moment_id).first()
        if not preset:
            raise HTTPException(status_code=404, detail="Preset moment not found")
    pos = db.query(ServiceMoment).filter(ServiceMoment.service_id == service_id).count() + 1 if payload.position is None else payload.position
    t = datetime.strptime(payload.time, "%H:%M").time() if payload.time else None
    m = ServiceMoment(service_id=service_id, position=pos, title=payload.title, responsible=payload.responsible, time=t, notes=payload.notes, moment_id=payload.moment_id, responsible_member_id=payload.responsible_member_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/api/services/{service_id}/moments/{moment_id}", response_model=MomentRead)
def update_moment(service_id: int, moment_id: int, payload: MomentUpdate, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    get_service_or_404(db, leader.church_id, service_id)
    m = db.query(ServiceMoment).filter(ServiceMoment.id == moment_id, ServiceMoment.service_id == service_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Moment not found")
    if payload.title is not None:
        m.title = payload.title
    if payload.responsible is not None:
        m.responsible = payload.responsible
    if payload.time is not None:
        m.time = datetime.strptime(payload.time, "%H:%M").time() if payload.time else None
    if payload.notes is not None:
        m.notes = payload.notes
    if payload.position is not None:
        m.position = payload.position
    if payload.moment_id is not None:
        preset = db.query(Moment).filter(Moment.id == payload.moment_id).first()
        if not preset:
            raise HTTPException(status_code=404, detail="Preset moment not found")
        m.moment_id = payload.moment_id
    if payload.responsible_member_id is not None:
        m.responsible_member_id = payload.responsible_member_id
    db.commit()
    db.refresh(m)
    return m


@router.delete("/api/services/{service_id}/moments/{moment_id}", status_code=204)
def delete_moment(service_id: int, moment_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    get_service_or_404(db, leader.church_id, service_id)
    m = db.query(ServiceMoment).filter(ServiceMoment.id == moment_id, ServiceMoment.service_id == service_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Moment not found")
    db.delete(m)
    db.commit()
    return


@router.get("/api/services/{service_id}/preset-moments")
def service_preset_moments(service_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    service = get_service_or_404(db, leader.church_id, service_id)

    template_ids: list[int] = []
    if getattr(service, "template_id", None):
        template_ids = [service.template_id]
    else:
        template_ids = [tid for (tid,) in (
            db.query(Moment.template_id)
            .join(ServiceMoment, ServiceMoment.moment_id == Moment.id)
            .filter(ServiceMoment.service_id == service_id, Moment.template_id.isnot(None))
            .distinct()
            .all()
        ) if tid is not None]

    if not template_ids:
        matched_moment_ids = [mid for (mid,) in (
            db.query(Moment.id)
            .join(ServiceMoment, func.lower(ServiceMoment.title) == func.lower(Moment.name))
            .filter(ServiceMoment.service_id == service_id)
            .distinct()
            .all()
        )]
        if matched_moment_ids:
            template_ids = [tid for (tid,) in db.query(Moment.template_id).filter(Moment.id.in_(matched_moment_ids), Moment.template_id.isnot(None)).distinct().all() if tid is not None]

    query = db.query(Moment).filter(Moment.is_active == True)
    if template_ids:
        template_names = {(name or "").strip().lower() for (name,) in db.query(Template.name).filter(Template.id.in_(template_ids)).all()}
        if "livre" not in template_names:
            query = query.filter(Moment.template_id.in_(template_ids))

    moments = query.order_by(Moment.position, Moment.name).all()
    return [{"id": m.id, "name": m.name, "position": m.position, "duration_min": m.duration_min, "template_id": m.template_id} for m in moments]


@router.get("/api/services/{service_id}/moments.csv")
def export_moments_csv(service_id: int, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    get_service_or_404(db, leader.church_id, service_id)
    rows = db.query(ServiceMoment).filter(ServiceMoment.service_id == service_id).order_by(ServiceMoment.position).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Position", "Time", "Title", "Responsible", "Notes"])
    for m in rows:
        responsible_display = (m.responsible or (m.responsible_member.name if getattr(m, "responsible_member", None) else "")) or ""
        writer.writerow([m.position, m.time.strftime("%H:%M") if m.time else "", m.title, responsible_display, m.notes or ""])
    return Response(content=buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=service_{service_id}_schedule.csv"})


@router.get("/api/members", response_model=list[MemberRead])
def list_members(q: str | None = None, active: bool = True, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    query = db.query(Member)
    if active:
        query = query.filter(Member.is_active == True)
    if q:
        ilike = f"%{q}%"
        query = query.filter(func.lower(Member.name).like(func.lower(ilike)))
    return query.order_by(Member.name).limit(20).all()


@router.post("/api/members", response_model=MemberRead)
def create_member(payload: MemberCreate, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    m = Member(name=payload.name.strip())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.post("/api/members/ensure", response_model=MemberRead)
def ensure_member(payload: MemberCreate, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    name = payload.name.strip()
    m = db.query(Member).filter(func.lower(Member.name) == func.lower(name)).first()
    if m:
        return m
    m = Member(name=name)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.get("/api/services/upcoming")
def upcoming_services(limit: int = 5, db: Session = Depends(get_db), leader: Leader = Depends(get_current_leader)):
    from datetime import date as dt_date

    today = dt_date.today()
    q = db.query(Service).filter(Service.church_id == leader.church_id).filter(func.date(Service.service_date) >= today).order_by(Service.service_date).limit(limit).all()
    return [{"id": s.id, "date": s.service_date.strftime("%Y-%m-%d"), "time": (s.start_time or s.service_time).strftime("%H:%M") if (s.start_time or s.service_time) else None, "preacher": s.preacher, "leader": s.leader, "title": s.title} for s in q]
