from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def checkin_page(request: Request):
    """Landing page with emotional check-in assessment."""
    return templates.TemplateResponse("checkin.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Main conversation page - opens with optional assessment context."""
    conversation_id = request.query_params.get("conversation_id", "")
    return templates.TemplateResponse(
        "chat.html", {"request": request, "conversation_id": conversation_id}
    )


@router.get("/dashboard/{conversation_id}", response_class=HTMLResponse)
async def dashboard_page(request: Request, conversation_id: str):
    """Dashboard page showing emotional analysis and wellness plan."""
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "conversation_id": conversation_id}
    )
