import logging
from fastapi import APIRouter, HTTPException
from api.services.pipeline_service import PipelineService
from api.models.requests import StartChatRequest, ContinueChatRequest, ConfirmPlanRequest
from api.models.responses import StartChatResponse, ContinueChatResponse, ConfirmPlanResponse

logger = logging.getLogger("chat_router")
router = APIRouter(prefix="/chat", tags=["Chat"])
pipeline_service = PipelineService()


# ─────────────────────────────────────────
# Start new session
# ─────────────────────────────────────────

@router.post("/start", response_model=StartChatResponse)
async def start_chat(request: StartChatRequest):
    """
    Start a new editing session.
    Called after user uploads files and types their first message.
    """
    try:
        logger.info(f"💬 Starting new chat session")
        logger.info(f"Prompt: {request.user_prompt[:50]}...")
        logger.info(f"Uploaded files: {list(request.uploaded_files.keys())}")

        result = await pipeline_service.start_session(
            user_prompt=request.user_prompt,
            video_placeholder=request.video_placeholder,
            image_placeholders=request.image_placeholders,
            audio_placeholder=request.audio_placeholder,
            uploaded_files=request.uploaded_files,   # ← THIS WAS MISSING
        )

        return StartChatResponse(**result)

    except ValueError as e:
        logger.warning(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ start_chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to start session. Please try again."
        )


# ─────────────────────────────────────────
# Continue session
# ─────────────────────────────────────────

@router.post("/message", response_model=ContinueChatResponse)
async def send_message(request: ContinueChatRequest):
    """
    Send a follow-up message in an existing session.
    """
    try:
        logger.info(f"💬 Message in session {request.session_id}")
        logger.info(f"Message: {request.message[:50]}...")

        result = await pipeline_service.continue_session(
            session_id=request.session_id,
            user_message=request.message
        )

        return ContinueChatResponse(**result)

    except ValueError as e:
        logger.warning(f"❌ Session not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ send_message failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )


# ─────────────────────────────────────────
# Confirm or reject plan
# ─────────────────────────────────────────

@router.post("/confirm", response_model=ConfirmPlanResponse)
async def confirm_plan(request: ConfirmPlanRequest):
    """
    Confirm or reject the plan shown to user.
    """
    try:
        logger.info(
            f"{'✅ Confirming' if request.confirmed else '🔄 Rejecting'} "
            f"plan for session {request.session_id}"
        )

        result = await pipeline_service.confirm_plan(
            session_id=request.session_id,
            confirmed=request.confirmed,
            feedback=request.feedback
        )

        return ConfirmPlanResponse(**result)

    except ValueError as e:
        logger.warning(f"❌ Session not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ confirm_plan failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process confirmation. Please try again."
        )