import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from components.video_player import video_player, execution_steps_display


def show():
    error = st.session_state.get("error")

    # ── Failed
    if error:
        st.markdown("## ❌ Something Went Wrong")
        st.error(error)
        execution_steps_display(st.session_state.get("execution_steps", []))

        if st.button("← Try Again", type="primary"):
            _reset()

        return

    # ── Done
    st.markdown("## ✅ Your Video is Ready!")
    st.balloons()

    url = st.session_state.get("final_video_url")
    if url:
        video_player(url)
    else:
        st.warning("Video URL not available.")

    st.divider()
    execution_steps_display(st.session_state.get("execution_steps", []))

    st.divider()
    if st.button("🎬 Edit Another Video", type="primary", use_container_width=True):
        _reset()


def _reset():
    """Clear all session state and go back to upload"""
    keys_to_clear = [
        "page", "session_id", "session_status", "user_prompt",
        "uploaded_files", "chat_history", "current_plan",
        "final_video_url", "execution_steps", "error",
        "uploaded_video", "uploaded_video_name",
        "uploaded_images", "uploaded_image_names",
        "uploaded_audio", "uploaded_audio_name",
        "show_feedback_input", "last_response",
        "image_placeholders", "audio_placeholder", "video_placeholder"
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.session_state["page"] = "upload"
    st.rerun()