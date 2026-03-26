import base64
import hashlib
import hmac
import os

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import Leader


SESSION_LEADER_KEY = "leader_id"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return base64.b64encode(salt + derived).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    raw = base64.b64decode(password_hash.encode("ascii"))
    salt = raw[:16]
    expected = raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(actual, expected)


def get_current_leader(request: Request, db: Session = Depends(get_db)) -> Leader:
    leader_id = request.session.get(SESSION_LEADER_KEY)
    if not leader_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    leader = db.query(Leader).get(leader_id)
    if not leader or not leader.is_active:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Authentication required")
    return leader


def get_optional_leader(request: Request, db: Session = Depends(get_db)) -> Leader | None:
    leader_id = request.session.get(SESSION_LEADER_KEY)
    if not leader_id:
        return None
    leader = db.query(Leader).get(leader_id)
    if not leader or not leader.is_active:
        request.session.clear()
        return None
    return leader


def login_leader(request: Request, leader: Leader) -> None:
    request.session[SESSION_LEADER_KEY] = leader.id
    request.session["leader_name"] = leader.name
    request.session["church_name"] = leader.church.name if leader.church else ""
    request.session["leader_role"] = leader.role


def logout_leader(request: Request) -> None:
    request.session.clear()
