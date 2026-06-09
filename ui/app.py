import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from api_client import APIClient

# ── Page config
st.set_page_config(
    page_title="Video Editing Agent",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Init session state
if "page" not in st.session_state:
    st.session_state["page"] = "upload"

# ── Header
st.markdown(
    """
    <h1 style='text-align:center; margin-bottom: 0'>🎬 Video Editing Agent</h1>
    <p style='text-align:center; color: gray; margin-top: 4px'>
        AI-powered video editing — just describe what you want
    </p>
    """,
    unsafe_allow_html=True
)

# ── API health check
client = APIClient()
health = client.health_check()
if health.get("status") != "ok":
    st.warning("⚠️ Cannot reach the API at http://localhost:8000 — make sure FastAPI is running.")

# ── Progress indicator
page = st.session_state["page"]
steps = ["upload", "chat", "result"]
step_labels = ["1 · Upload", "2 · Chat", "3 · Result"]
current = steps.index(page) if page in steps else 0

cols = st.columns(3)
for i, (col, label) in enumerate(zip(cols, step_labels)):
    with col:
        if i < current:
            st.markdown(f"<p style='text-align:center;color:#4CAF50'>✓ {label}</p>", unsafe_allow_html=True)
        elif i == current:
            st.markdown(f"<p style='text-align:center;font-weight:bold'>{label}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align:center;color:gray'>{label}</p>", unsafe_allow_html=True)

st.divider()

# ── Route to page
if page == "upload":
    from pages.upload_page import show
    show()
elif page == "chat":
    from pages.chat_page import show
    show()
elif page == "result":
    from pages.result_page import show
    show()