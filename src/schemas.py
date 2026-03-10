import datetime as dt
from pydantic import BaseModel


class SongInsert(BaseModel):
    title: str
    hymn_number: int
    misc: str


class SongRead(BaseModel):
    id: int
    title: str
    hymn_number: int
    misc: str

    class Config:
        from_attributes = True


# Service update payload for quick edits
class ServiceUpdate(BaseModel):
    service_date: str | None = None
    # legacy single time (mapped to start_time if provided)
    service_time: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    preacher: str | None = None
    leader: str | None = None
    title: str | None = None
    notes: str | None = None


# Members
class MemberCreate(BaseModel):
    name: str

class MemberRead(BaseModel):
    id: int
    name: str
    is_active: bool
    class Config:
        from_attributes = True


# Moments (schedule)
class MomentBase(BaseModel):
    title: str
    responsible: str | None = None
    time: str | None = None  # HH:MM
    notes: str | None = None

class MomentCreate(MomentBase):
    position: int | None = None  # append if not provided
    responsible_member_id: int | None = None

class MomentUpdate(BaseModel):
    title: str | None = None
    responsible: str | None = None
    time: str | None = None
    notes: str | None = None
    position: int | None = None
    responsible_member_id: int | None = None

class MomentRead(BaseModel):
    id: int
    position: int
    title: str
    responsible: str | None
    time: dt.time | None
    notes: str | None
    responsible_member_id: int | None = None
    class Config:
        from_attributes = True
