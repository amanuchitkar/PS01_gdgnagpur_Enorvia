from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.conversation_service import conversation_service
from app.services.pdf_service import pdf_service
from app.repositories import PDFReportRepository

router = APIRouter(prefix="/api", tags=["api"])
pdf_report_repo = PDFReportRepository()


class MessageRequest(BaseModel):
    conversation_id: str
    message: str


class EndConversationRequest(BaseModel):
    conversation_id: str


class CheckinStartRequest(BaseModel):
    score: int
    max_score: int
    category: str
    concerns: list[str] = []
    emotional_summary: str = ""
    area_scores: dict = {}


@router.post("/conversation/start")
async def start_conversation(db: AsyncSession = Depends(get_db)):
    """Start a new conversation session."""
    conversation = await conversation_service.create_conversation(db)
    return {"conversation_id": conversation.id, "status": "active"}


@router.post("/conversation/start-with-checkin")
async def start_conversation_with_checkin(
    request: CheckinStartRequest, db: AsyncSession = Depends(get_db)
):
    """Start a new conversation with emotional check-in context.

    The check-in results are passed to the AI as initial context so the
    companion can begin with relevant awareness of the user's state.
    """
    try:
        conversation = await conversation_service.create_conversation_with_checkin(
            db,
            score=request.score,
            max_score=request.max_score,
            category=request.category,
            concerns=request.concerns,
            emotional_summary=request.emotional_summary,
            area_scores=request.area_scores,
        )
        return {"conversation_id": conversation.id, "status": "active"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting conversation: {str(e)}"
        )


@router.post("/conversation/message")
async def send_message(request: MessageRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and get AI analysis."""
    try:
        result = await conversation_service.process_message(
            db, request.conversation_id, request.message
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/conversation/{conversation_id}/messages")
async def get_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages for a conversation (used to restore chat state)."""
    try:
        conversation = await conversation_service.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages
        ]
        return {"conversation_id": conversation_id, "messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")


@router.post("/conversation/end")
async def end_conversation(request: EndConversationRequest, db: AsyncSession = Depends(get_db)):
    """End a conversation and generate wellness plan."""
    try:
        result = await conversation_service.end_conversation(db, request.conversation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending conversation: {str(e)}")


@router.get("/dashboard/{conversation_id}")
async def get_dashboard(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get dashboard data for a conversation."""
    try:
        result = await conversation_service.get_dashboard_data(db, conversation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")


@router.get("/report/{conversation_id}/pdf")
async def download_pdf_report(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Generate and download a PDF wellness report for a conversation."""
    try:
        # Get dashboard data (same data used for the web dashboard)
        dashboard_data = await conversation_service.get_dashboard_data(db, conversation_id)

        # Generate PDF
        pdf_bytes, filename = pdf_service.generate_report(dashboard_data)

        # Save to disk and record in database
        file_path = pdf_service.save_report(pdf_bytes, filename)
        await pdf_report_repo.create(
            db,
            conversation_id=conversation_id,
            filename=filename,
            file_path=file_path,
            report_type="full",
            file_size_bytes=len(pdf_bytes),
        )
        await db.commit()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
