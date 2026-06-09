import streamlit as st
from api_client import APIClient

client = APIClient()


def video_uploader() -> dict | None:
    """Returns upload result dict or None"""
    st.markdown("#### 🎬 Video")
    st.caption("MP4 or MOV — max 200MB")

    file = st.file_uploader("Upload video", type=["mp4", "mov"], key="video_upload", label_visibility="collapsed")
    if file:
        if st.session_state.get("uploaded_video_name") == file.name:
            return st.session_state.get("uploaded_video")

        with st.spinner(f"Uploading {file.name}..."):
            try:
                result = client.upload_video(file.read(), file.name)
                st.session_state["uploaded_video"] = result
                st.session_state["uploaded_video_name"] = file.name
                st.success(f"✅ {file.name} uploaded")
                return result
            except Exception as e:
                st.error(f"Upload failed: {e}")
    return None


def image_uploader() -> list[dict]:
    """Returns list of upload result dicts"""
    st.markdown("#### 🖼️ Images (optional)")
    st.caption("JPG, PNG, WEBP — max 10MB each — up to 4 images")

    files = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="image_upload",
        label_visibility="collapsed"
    )

    if not files:
        return []

    if len(files) > 4:
        st.error("Maximum 4 images allowed.")
        return []

    # check if same files already uploaded
    names = [f.name for f in files]
    if st.session_state.get("uploaded_image_names") == names:
        return st.session_state.get("uploaded_images", [])

    with st.spinner(f"Uploading {len(files)} image(s)..."):
        try:
            file_tuples = [(f.name, f.read()) for f in files]
            results = client.upload_multiple_images(file_tuples)
            st.session_state["uploaded_images"] = results
            st.session_state["uploaded_image_names"] = names
            st.success(f"✅ {len(results)} image(s) uploaded")
            return results
        except Exception as e:
            st.error(f"Upload failed: {e}")
    return []


def audio_uploader() -> dict | None:
    """Returns upload result dict or None"""
    st.markdown("#### 🎵 Audio (optional)")
    st.caption("MP3, WAV, OGG, M4A, AAC — max 50MB")

    file = st.file_uploader(
        "Upload audio",
        type=["mp3", "wav", "ogg", "m4a", "aac"],
        key="audio_upload",
        label_visibility="collapsed"
    )

    if file:
        if st.session_state.get("uploaded_audio_name") == file.name:
            return st.session_state.get("uploaded_audio")

        with st.spinner(f"Uploading {file.name}..."):
            try:
                result = client.upload_audio(file.read(), file.name)
                st.session_state["uploaded_audio"] = result
                st.session_state["uploaded_audio_name"] = file.name
                st.success(f"✅ {file.name} uploaded")
                return result
            except Exception as e:
                st.error(f"Upload failed: {e}")
    return None