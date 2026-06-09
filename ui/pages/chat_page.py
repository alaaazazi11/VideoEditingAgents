import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from api_client import APIClient
from components.chat_bubble import chat_bubble, render_chat_history, add_to_history
from components.plan_card import plan_card

client = APIClient()


def _handle_response(response: dict):
    """Process API response and update session state accordingly"""
    status = response.get("status")
    message = response.get("message")
    plan = response.get("plan")

    st.session_state["session_status"] = status
    st.session_state["current_plan"] = plan
    st.session_state["last_response"] = response

    if message:
        add_to_history("assistant", message)

    if status == "done":
        st.session_state["final_video_url"] = response.get("final_video_url")
        st.session_state["execution_steps"] = response.get("execution_steps", [])
        st.session_state["page"] = "result"
        st.rerun()

    if status == "failed":
        st.session_state["error"] = response.get("error", "Unknown error")
        st.session_state["execution_steps"] = response.get("execution_steps", [])
        st.session_state["page"] = "result"
        st.rerun()


def show():
    st.markdown("## Step 2 — Chat with the Agent")

    # back button
    if st.button("← Back to Upload"):
        st.session_state["page"] = "upload"
        st.session_state["session_id"] = None
        st.session_state["session_status"] = None
        st.rerun()

    st.divider()

    # ── Start session if not started yet
    if not st.session_state.get("session_id"):
        prompt = st.session_state.get("user_prompt", "")
        add_to_history("user", prompt)

        with st.spinner("🤖 Agent is analyzing your request..."):
            try:
                response = client.start_chat(
                    user_prompt=prompt,
                    uploaded_files=st.session_state.get("uploaded_files", {}),
                    video_placeholder=st.session_state.get("video_placeholder", "@Video1"),
                    image_placeholders=st.session_state.get("image_placeholders", []),
                    audio_placeholder=st.session_state.get("audio_placeholder"),
                )
                st.session_state["session_id"] = response["session_id"]
                _handle_response(response)
            except Exception as e:
                st.error(f"Failed to start session: {e}")
                return

    # ── Render chat history
    render_chat_history()

    # ── Plan confirmation
    status = st.session_state.get("session_status")
    if status == "awaiting_plan_confirmation":
        plan = st.session_state.get("current_plan")
        confirmed, feedback = plan_card(plan)

        if confirmed is not None:
            session_id = st.session_state["session_id"]
            user_msg = "✅ Confirmed" if confirmed else f"🔄 Changes: {feedback}"
            add_to_history("user", user_msg)

            with st.spinner("🤖 Processing..."):
                try:
                    response = client.confirm_plan(session_id, confirmed, feedback)
                    _handle_response(response)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

    # ── Normal chat input (collecting params)
    elif status == "collecting" or status is None:
        session_id = st.session_state.get("session_id")
        if session_id:
            user_input = st.chat_input("Your reply...")
            if user_input:
                add_to_history("user", user_input)
                chat_bubble("user", user_input)

                with st.spinner("🤖 Thinking..."):
                    try:
                        response = client.send_message(session_id, user_input)
                        _handle_response(response)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")