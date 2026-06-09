import logging
from typing import Optional
from graph.graph_builder import build_graph
from state.shared_state import SharedState
from api.services.session_service import SessionService
from api.services.file_service import FileService

logger = logging.getLogger("pipeline_service")


class PipelineService:
    """
    Orchestrates the full pipeline:
    Routing Agent → Planning Agent → Feature Agents → Execution Agent

    Called by chat router after each user message.
    Updates session state and returns what to show the user next.
    """

    def __init__(self):
        self.session_service = SessionService()
        self.file_service = FileService()
        self.graph = build_graph()

    # ─────────────────────────────────────────
    # Start new session
    # ─────────────────────────────────────────

    async def start_session(
        self,
        user_prompt: str,
        video_placeholder: str,
        image_placeholders: list[str] = [],
        audio_placeholder: Optional[str] = None,
        uploaded_files: dict[str, str] = {},  # {"@Video1": "url", "@Image1": "url"}
    ) -> dict:
        """
        uploaded_files: dict of placeholder → URL from upload endpoints
        """
        try:
            # file_references already built from uploaded files
            file_references = uploaded_files

            # get video metadata from video URL
            video_url = file_references.get(video_placeholder, "")
            video_metadata = await self.file_service.get_video_metadata_from_url(video_url)

            # create session
            session_id = self.session_service.create_session(
                user_prompt=user_prompt,
                video_metadata=video_metadata,
                file_references=file_references,
            )

            # run graph
            state = self.session_service.get_shared_state(session_id)
            state = await self.graph.ainvoke(state)
            self.session_service.update_shared_state(session_id, state)

            return self._build_response(session_id, state)

        except Exception as e:
            logger.error(f"❌ start_session failed: {e}")
            raise

    # ─────────────────────────────────────────
    # Continue session (user reply)
    # ─────────────────────────────────────────

    async def continue_session(
        self,
        session_id: str,
        user_message: str
    ) -> dict:
        """
        Called when user sends a follow-up message.
        Updates state and runs graph again.
        """
        if not self.session_service.session_exists(session_id):
            raise ValueError(f"Session {session_id} not found")

        try:
            # update state with user reply
            self.session_service.update_user_reply(session_id, user_message)

            # get updated state and run graph
            state = self.session_service.get_shared_state(session_id)
            state = await self.graph.ainvoke(state)
            self.session_service.update_shared_state(session_id, state)

            return self._build_response(session_id, state)

        except Exception as e:
            logger.error(f"❌ continue_session failed: {e}")
            raise

    # ─────────────────────────────────────────
    # Confirm plan
    # ─────────────────────────────────────────

    async def confirm_plan(
        self,
        session_id: str,
        confirmed: bool,
        feedback: Optional[str] = None
    ) -> dict:
        """
        Called when user confirms or rejects the plan.
        """
        if not self.session_service.session_exists(session_id):
            raise ValueError(f"Session {session_id} not found")

        try:
            if confirmed:
                self.session_service.confirm_plan(session_id)
            else:
                self.session_service.request_plan_changes(
                    session_id=session_id,
                    feedback=feedback or "Please revise the plan"
                )

            # run graph again
            state = self.session_service.get_shared_state(session_id)
            state = await self.graph.ainvoke(state)
            self.session_service.update_shared_state(session_id, state)

            return self._build_response(session_id, state)

        except Exception as e:
            logger.error(f"❌ confirm_plan failed: {e}")
            raise

    # ─────────────────────────────────────────
    # Build response
    # ─────────────────────────────────────────

    def _build_response(self, session_id: str, state: SharedState) -> dict:
        """
        Build response dict based on current state.
        Determines what to show the user next.
        """
        # ── Execution done ✅
        if state.get("execution_status") == "done":
            self.session_service.set_status(session_id, "done")
            return {
                "session_id": session_id,
                "status": "done",
                "message": "🎉 Your video is ready!",
                "final_video_url": state.get("execution_output_url"),
                "execution_steps": state.get("execution_steps", []),
            }

        # ── Execution failed ❌
        if state.get("execution_status") == "failed":
            self.session_service.set_status(session_id, "failed")
            return {
                "session_id": session_id,
                "status": "failed",
                "message": "❌ Something went wrong during processing.",
                "error": state.get("execution_error"),
                "execution_steps": state.get("execution_steps", []),
            }

        # ── Awaiting plan confirmation
        if state.get("plan_status") == "awaiting_confirmation":
            self.session_service.set_status(session_id, "awaiting_plan_confirmation")
            return {
                "session_id": session_id,
                "status": "awaiting_plan_confirmation",
                "message": state.get("latest_assistant_message"),
                "plan": state.get("plan"),
            }

        # ── Collecting params (agent asking for more info)
        if state.get("latest_assistant_message"):
            self.session_service.set_status(session_id, "collecting")
            return {
                "session_id": session_id,
                "status": "collecting",
                "message": state.get("latest_assistant_message"),
            }

        # ── Fallback
        return {
            "session_id": session_id,
            "status": "collecting",
            "message": None,
        }