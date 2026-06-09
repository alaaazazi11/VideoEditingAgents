import uuid
import logging
from typing import Optional
from state.shared_state import SharedState, AgentStatus

logger = logging.getLogger("session_service")

# ─────────────────────────────────────────
# In-memory session store
# In production → replace with Redis
# ─────────────────────────────────────────
sessions: dict[str, dict] = {}


class SessionService:

    # ─────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────

    def create_session(
        self,
        user_prompt: str,
        video_metadata: dict,
        file_references: dict,
    ) -> str:
        """
        Create a new session and initialize shared state.
        Returns session_id.
        """
        session_id = str(uuid.uuid4())

        sessions[session_id] = {
            "session_id": session_id,
            "status": "collecting",
            "shared_state": self._build_initial_state(
                user_prompt=user_prompt,
                video_metadata=video_metadata,
                file_references=file_references,
            )
        }

        logger.info(f"✅ Created session {session_id}")
        return session_id

    def _build_initial_state(
        self,
        user_prompt: str,
        video_metadata: dict,
        file_references: dict,
    ) -> SharedState:
        """Build initial shared state for a new session"""
        return {
            # Input
            "user_prompt": user_prompt,
            "video_metadata": video_metadata,
            "file_references": file_references,

            # Routing Agent output
            "selected_features": [],
            "tier": "",
            "tier_reasoning": "",
            "basic_total_cost": 0.0,
            "kling_total_cost": 0.0,

            # Planning Agent output
            "plan": None,
            "plan_status": "awaiting_confirmation",
            "skip_planning": False,
            "user_plan_feedback": None,

            # Feature agents state
            "agents_state": {},

            # Conversation
            "conversation_history": [
                {"role": "user", "content": user_prompt}
            ],
            "latest_user_reply": user_prompt,
            "latest_assistant_message": "",

            # Execution Agent output
            "execution_status": "pending",
            "execution_output_url": "",
            "execution_error": None,
            "execution_steps": [],

            # Output
            "final_params": {}
        }

    # ─────────────────────────────────────────
    # Read
    # ─────────────────────────────────────────

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID"""
        session = sessions.get(session_id)
        if not session:
            logger.warning(f"❌ Session {session_id} not found")
        return session

    def get_shared_state(self, session_id: str) -> Optional[SharedState]:
        """Get shared state for a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session["shared_state"]

    def get_status(self, session_id: str) -> Optional[str]:
        """Get session status"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session["status"]

    # ─────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────

    def update_shared_state(
        self,
        session_id: str,
        shared_state: SharedState
    ) -> None:
        """Update shared state after graph invocation"""
        if session_id not in sessions:
            logger.warning(f"❌ Cannot update — session {session_id} not found")
            return
        sessions[session_id]["shared_state"] = shared_state
        logger.info(f"Updated shared state for session {session_id}")

    def set_status(self, session_id: str, status: str) -> None:
        """Update session status"""
        if session_id not in sessions:
            return
        sessions[session_id]["status"] = status
        logger.info(f"Session {session_id} → status: {status}")

    def update_user_reply(
        self,
        session_id: str,
        user_reply: str
    ) -> None:
        """
        Update latest user reply and conversation history.
        Called before re-invoking the graph.
        """
        session = self.get_session(session_id)
        if not session:
            return

        state = session["shared_state"]
        state["latest_user_reply"] = user_reply
        state["conversation_history"].append({
            "role": "user",
            "content": user_reply
        })
        self.update_shared_state(session_id, state)
        logger.info(f"Session {session_id} — user replied: {user_reply[:50]}...")

    def confirm_plan(self, session_id: str) -> None:
        """
        Handle plan confirmation.
        Resets agents state and sets skip_planning flag.
        """
        session = self.get_session(session_id)
        if not session:
            return

        state = session["shared_state"]
        state["plan_status"] = "confirmed"
        state["skip_planning"] = True
        state["user_plan_feedback"] = None
        state["agents_state"] = {}
        state["latest_user_reply"] = (
            "Confirmed — please proceed with: " + state["user_prompt"]
        )
        state["conversation_history"].append({
            "role": "user",
            "content": "Confirmed — please proceed with: " + state["user_prompt"]
        })
        self.update_shared_state(session_id, state)
        self.set_status(session_id, "confirmed")
        logger.info(f"Session {session_id} — plan confirmed")

    def request_plan_changes(
        self,
        session_id: str,
        feedback: str
    ) -> None:
        """
        Handle plan change request.
        Resets planning and sets feedback.
        """
        session = self.get_session(session_id)
        if not session:
            return

        state = session["shared_state"]
        state["plan_status"] = "changes_requested"
        state["skip_planning"] = False
        state["user_plan_feedback"] = feedback
        state["conversation_history"].append({
            "role": "user",
            "content": feedback
        })
        self.update_shared_state(session_id, state)
        self.set_status(session_id, "changes_requested")
        logger.info(f"Session {session_id} — plan changes requested: {feedback[:50]}...")

    # ─────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────

    def delete_session(self, session_id: str) -> None:
        """Delete session after it's done"""
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"🗑️ Deleted session {session_id}")

    # ─────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────

    def session_exists(self, session_id: str) -> bool:
        return session_id in sessions

    def get_final_video_url(self, session_id: str) -> Optional[str]:
        """Get final video URL when execution is done"""
        state = self.get_shared_state(session_id)
        if not state:
            return None
        return state.get("execution_output_url")

    def get_plan(self, session_id: str) -> Optional[dict]:
        """Get plan details for display"""
        state = self.get_shared_state(session_id)
        if not state:
            return None
        return state.get("plan")