from fastapi import APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy import text

from src.db.base import engine


router = APIRouter()


@router.get("/health")
def health_root():
    return {"ok": True}


@router.get("/db/health")
def health_db():
    try:
        with engine.connect() as conn:
            # Minimal query; if DB is down, will raise within connect_timeout
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=503, content={"ok": False, "error": str(e)})
