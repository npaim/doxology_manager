from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.db.base import get_db

router = APIRouter()
_templates = Jinja2Templates(directory="src/templates")


@router.get("/services/new-with-template", response_class=HTMLResponse)
async def new_service_with_template_alias(
    request: Request,
    template_id: int,
    date: str | None = None,
    db: Session = Depends(get_db),
):
    from src.db.models import Moment
    preset_moments = (
        db.query(Moment)
        .filter(Moment.template_id == template_id, Moment.is_active == True, Moment.default_moment == True)
        .order_by(Moment.position, Moment.name)
        .all()
    )
    extra_moments = (
        db.query(Moment)
        .filter(Moment.template_id == template_id, Moment.is_active == True, Moment.default_moment == False)
        .order_by(Moment.position, Moment.name)
        .all()
    )
    return _templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service_date": date,
            "start_time": "",
            "end_time": "",
            "preset_moments": preset_moments,
            "extra_moments": extra_moments,
            "selected_template_id": template_id,
        },
    )

