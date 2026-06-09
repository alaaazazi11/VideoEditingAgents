import requests
from typing import Optional

BASE_URL = "http://localhost:8000"


class APIClient:

    # ─────────────────────────────────────────
    # Upload
    # ─────────────────────────────────────────

    def upload_video(self, file_bytes: bytes, filename: str, placeholder: str = "@Video1") -> dict:
        response = requests.post(
            f"{BASE_URL}/upload/video",
            files={"file": (filename, file_bytes)},
            params={"placeholder": placeholder}
        )
        response.raise_for_status()
        return response.json()

    def upload_image(self, file_bytes: bytes, filename: str, placeholder: str = "@Image1") -> dict:
        response = requests.post(
            f"{BASE_URL}/upload/image",
            files={"file": (filename, file_bytes)},
            params={"placeholder": placeholder}
        )
        response.raise_for_status()
        return response.json()

    def upload_multiple_images(self, files: list[tuple[str, bytes]]) -> list[dict]:
        response = requests.post(
            f"{BASE_URL}/upload/images",
            files=[("files", (name, data)) for name, data in files]
        )
        response.raise_for_status()
        return response.json()

    def upload_audio(self, file_bytes: bytes, filename: str, placeholder: str = "@Audio1") -> dict:
        response = requests.post(
            f"{BASE_URL}/upload/audio",
            files={"file": (filename, file_bytes)},
            params={"placeholder": placeholder}
        )
        response.raise_for_status()
        return response.json()

    # ─────────────────────────────────────────
    # Chat
    # ─────────────────────────────────────────

    def start_chat(
        self,
        user_prompt: str,
        uploaded_files: dict[str, str],
        video_placeholder: str = "@Video1",
        image_placeholders: list[str] = [],
        audio_placeholder: Optional[str] = None,
    ) -> dict:
        response = requests.post(
            f"{BASE_URL}/chat/start",
            json={
                "user_prompt": user_prompt,
                "uploaded_files": uploaded_files,
                "video_placeholder": video_placeholder,
                "image_placeholders": image_placeholders,
                "audio_placeholder": audio_placeholder,
            }
        )
        response.raise_for_status()
        return response.json()

    def send_message(self, session_id: str, message: str) -> dict:
        response = requests.post(
            f"{BASE_URL}/chat/message",
            json={"session_id": session_id, "message": message}
        )
        response.raise_for_status()
        return response.json()

    def confirm_plan(self, session_id: str, confirmed: bool, feedback: Optional[str] = None) -> dict:
        response = requests.post(
            f"{BASE_URL}/chat/confirm",
            json={"session_id": session_id, "confirmed": confirmed, "feedback": feedback}
        )
        response.raise_for_status()
        return response.json()

    # ─────────────────────────────────────────
    # Health
    # ─────────────────────────────────────────

    def health_check(self) -> dict:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            return response.json()
        except Exception:
            return {"status": "unreachable"}