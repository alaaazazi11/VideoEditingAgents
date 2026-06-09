import streamlit as st


def chat_bubble(role: str, message: str):
    """Display a chat message bubble. role: 'user' or 'assistant'"""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message)
    else:
        with st.chat_message("assistant", avatar="🎬"):
            st.markdown(message)


def render_chat_history():
    """Render all messages from session state"""
    for msg in st.session_state.get("chat_history", []):
        chat_bubble(msg["role"], msg["content"])


def add_to_history(role: str, content: str):
    """Append a message to chat history in session state"""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    st.session_state["chat_history"].append({"role": role, "content": content})