from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import Moment, Template
from src.routers.pages import require_page_leader

router = APIRouter()
_templates = Jinja2Templates(directory="src/templates")


@router.get("/services/new-with-template", response_class=HTMLResponse)
async def new_service_with_template_alias(
    request: Request,
    template_id: int,
    date: str | None = None,
    db: Session = Depends(get_db),
):
    leader = require_page_leader(request, db)
    if isinstance(leader, RedirectResponse):
        return leader

    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return RedirectResponse("/services/new/choose", status_code=303)

    preset_moments = (
        db.query(Moment)
        .filter(Moment.template_id == template_id, Moment.is_active == True, Moment.default_moment == True)
        .order_by(Moment.position, Moment.name)
        .all()
    )
    is_livre = bool((template.name or "").strip().lower() == "livre")
    extra_moments_query = db.query(Moment).filter(Moment.is_active == True)
    if not is_livre:
        extra_moments_query = extra_moments_query.filter(Moment.template_id == template_id)

    return _templates.TemplateResponse(
        "service_form.html",
        {
            "request": request,
            "service_date": date,
            "start_time": "",
            "end_time": "",
            "preset_moments": preset_moments,
            "extra_moments": extra_moments_query.order_by(Moment.position, Moment.name).all(),
            "selected_template_id": template_id,
            "selected_template_name": template.name,
        },
    )
