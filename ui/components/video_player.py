import streamlit as st
import requests


def video_player(url: str, title: str = "Your edited video"):
    """Display a video player with a download button"""
    st.markdown(f"### 🎉 {title}")
    st.video(url)

    # download button — fetch bytes from URL
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            with st.spinner("Preparing download..."):
                video_bytes = requests.get(url, timeout=30).content
            st.download_button(
                label="⬇️ Download",
                data=video_bytes,
                file_name="edited_video.mp4",
                mime="video/mp4",
                use_container_width=True,
                type="primary"
            )
        except Exception:
            st.link_button("🔗 Open Video", url, use_container_width=True)


def execution_steps_display(steps: list[dict]):
    """Display execution steps as a timeline"""
    if not steps:
        return

    st.markdown("### ⚙️ Processing Steps")
    for i, step in enumerate(steps, 1):
        status = step.get("status", "")
        name = step.get("name", f"Step {i}")
        detail = step.get("detail", "")

        icon = "✅" if status == "done" else "❌" if status == "failed" else "🔄"
        st.markdown(f"{icon} **{name}**")
        if detail:
            st.caption(f"  {detail}")