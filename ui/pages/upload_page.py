import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from components.file_uploader import video_uploader, image_uploader, audio_uploader


def show():
    st.markdown("## Step 1 — Upload Your Files")
    st.caption("Upload your video and any extra assets. Then describe what you want done.")

    # ── File uploaders
    video_result = video_uploader()
    st.divider()
    image_results = image_uploader()
    st.divider()
    audio_result = audio_uploader()
    st.divider()

    # ── Build uploaded_files dict
    uploaded_files = {}
    image_placeholders = []

    if video_result:
        uploaded_files[video_result["placeholder"]] = video_result["url"]

    for img in image_results:
        uploaded_files[img["placeholder"]] = img["url"]
        image_placeholders.append(img["placeholder"])

    if audio_result:
        uploaded_files[audio_result["placeholder"]] = audio_result["url"]

    # save to session state for chat page
    st.session_state["uploaded_files"] = uploaded_files
    st.session_state["image_placeholders"] = image_placeholders
    st.session_state["audio_placeholder"] = audio_result["placeholder"] if audio_result else None
    st.session_state["video_placeholder"] = video_result["placeholder"] if video_result else "@Video1"

    # ── Prompt input
    st.markdown("#### ✏️ What do you want to do?")
    prompt = st.text_area(
        "Describe your editing request",
        placeholder='e.g. "Add subtitles in white, trim the first 5 seconds, and add background music from @Audio1"',
        height=100,
        label_visibility="collapsed"
    )

    # ── Start button
    ready = bool(video_result and prompt.strip())

    if not video_result:
        st.info("📹 Upload a video to get started.")

    if st.button(
        "🚀 Start Editing",
        disabled=not ready,
        use_container_width=True,
        type="primary"
    ):
        st.session_state["user_prompt"] = prompt.strip()
        st.session_state["page"] = "chat"
        st.session_state["chat_history"] = []
        st.rerun()