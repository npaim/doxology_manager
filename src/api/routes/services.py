from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from src.db.base import get_db
from src.db.models import Service, ServiceMoment, Member
from src.schemas import (
    ServiceUpdate,
    MomentCreate,
    MomentUpdate,
    MomentRead,
    MemberCreate,
    MemberRead,
)

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
                "start_time": (s.start_time or s.service_time).strftime("%H:%M") if (s.start_time or s.service_time) else None,
                "end_time": (s.end_time or s.service_time).strftime("%H:%M") if (s.end_time or s.service_time) else None,
                "preacher": s.preacher,
                "leader": s.leader,
                "title": s.title,
                "notes": s.notes,
            },
        })
    return result


@router.put("/api/services/{service_id}")
def update_service(service_id: int, payload: ServiceUpdate, db: Session = Depends(get_db)):
    s = db.query(Service).get(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")

    if payload.service_date is not None:
        s.service_date = datetime.strptime(payload.service_date, "%Y-%m-%d")

    # Support start/end times (and legacy service_time for start)
    if (payload.start_time is not None) or (payload.service_time is not None):
        st = payload.start_time or payload.service_time
        s.start_time = datetime.strptime(st, "%H:%M").time()
        s.service_time = s.start_time  # keep legacy in sync

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
def delete_service(service_id: int, db: Session = Depends(get_db)):
    s = db.query(Service).get(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(s)
    db.commit()
    return


# Moments (schedule) endpoints
@router.get("/api/services/{service_id}/moments", response_model=list[MomentRead])
def list_moments(service_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ServiceMoment)
        .filter(ServiceMoment.service_id == service_id)
        .order_by(ServiceMoment.position)
        .all()
    )


@router.post("/api/services/{service_id}/moments", response_model=MomentRead)
def create_moment(service_id: int, payload: MomentCreate, db: Session = Depends(get_db)):
    # ensure service exists
    s = db.query(Service).get(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")

    # compute position
    if payload.position is None:
        maxpos = db.query(ServiceMoment).filter(ServiceMoment.service_id == service_id).count()
        pos = maxpos + 1
    else:
        pos = payload.position

    t = datetime.strptime(payload.time, "%H:%M").time() if payload.time else None

    m = ServiceMoment(
        service_id=service_id,
        position=pos,
        title=payload.title,
        responsible=payload.responsible,
        time=t,
        notes=payload.notes,
        responsible_member_id=payload.responsible_member_id,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/api/services/{service_id}/moments/{moment_id}", response_model=MomentRead)
def update_moment(service_id: int, moment_id: int, payload: MomentUpdate, db: Session = Depends(get_db)):
    m = db.query(ServiceMoment).get(moment_id)
    if not m or m.service_id != service_id:
        raise HTTPException(status_code=404, detail="Moment not found")

    if payload.title is not None:
        m.title = payload.title
    if payload.responsible is not None:
        m.responsible = payload.responsible
    if payload.time is not None:
        m.time = datetime.strptime(payload.time, "%H:%M").time()
    if payload.notes is not None:
        m.notes = payload.notes
    if payload.position is not None:
        m.position = payload.position
    if getattr(payload, "responsible_member_id", None) is not None:
        m.responsible_member_id = payload.responsible_member_id

    db.commit()
    db.refresh(m)
    return m


@router.delete("/api/services/{service_id}/moments/{moment_id}", status_code=204)
def delete_moment(service_id: int, moment_id: int, db: Session = Depends(get_db)):
    m = db.query(ServiceMoment).get(moment_id)
    if not m or m.service_id != service_id:
        raise HTTPException(status_code=404, detail="Moment not found")
    db.delete(m)
    db.commit()
    return


# CSV export for moments
import csv
import io

@router.get("/api/services/{service_id}/moments.csv")
def export_moments_csv(service_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(ServiceMoment)
        .filter(ServiceMoment.service_id == service_id)
        .order_by(ServiceMoment.position)
        .all()
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Position", "Time", "Title", "Responsible", "Notes"])
    for m in rows:
        responsible_display = (m.responsible or (m.responsible_member.name if getattr(m, "responsible_member", None) else "")) or ""
        writer.writerow([
            m.position,
            m.time.strftime("%H:%M") if m.time else "",
            m.title,
            responsible_display,
            m.notes or "",
        ])
    data = buf.getvalue()
    headers = {"Content-Disposition": f"attachment; filename=service_{service_id}_schedule.csv"}
    return Response(content=data, media_type="text/csv", headers=headers)


# Members endpoints
@router.get("/api/members", response_model=list[MemberRead])
def list_members(q: str | None = None, active: bool = True, db: Session = Depends(get_db)):
    query = db.query(Member)
    if active:
        query = query.filter(Member.is_active == True)
    if q:
        ilike = f"%{q}%"
        query = query.filter(func.lower(Member.name).like(func.lower(ilike)))
    return query.order_by(Member.name).limit(20).all()


@router.post("/api/members", response_model=MemberRead)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    m = Member(name=payload.name.strip())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.post("/api/members/ensure", response_model=MemberRead)
def ensure_member(payload: MemberCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    m = db.query(Member).filter(func.lower(Member.name) == func.lower(name)).first()
    if m:
        return m
    m = Member(name=name)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
