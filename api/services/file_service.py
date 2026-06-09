import os
import asyncio
import logging
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

logger = logging.getLogger("file_service")


# ─────────────────────────────────────────
# Cloudinary config
# ─────────────────────────────────────────
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# ─────────────────────────────────────────
# Supported formats + size limits
# ─────────────────────────────────────────

SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov"}
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}

MAX_VIDEO_SIZE_MB = 200
MAX_IMAGE_SIZE_MB = 10
MAX_AUDIO_SIZE_MB = 50


# ─────────────────────────────────────────
# Custom exceptions
# ─────────────────────────────────────────

class FileValidationError(Exception):
    pass


# ─────────────────────────────────────────
# File Service
# ─────────────────────────────────────────

class FileService:

    # ─────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────

    def _get_size_mb(self, file_bytes: bytes) -> float:
        return len(file_bytes) / (1024 * 1024)

    def _get_format(self, filename: str) -> str:
        return Path(filename).suffix.lower()

    # ─────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────

    def validate_video(self, filename: str, file_bytes: bytes) -> None:
        fmt = self._get_format(filename)
        size_mb = self._get_size_mb(file_bytes)

        if fmt not in SUPPORTED_VIDEO_FORMATS:
            raise FileValidationError(
                f"Unsupported video format '{fmt}'. Only MP4 and MOV are supported."
            )
        if size_mb > MAX_VIDEO_SIZE_MB:
            raise FileValidationError(
                f"Video size {size_mb:.1f}MB exceeds maximum of {MAX_VIDEO_SIZE_MB}MB."
            )

    def validate_image(self, filename: str, file_bytes: bytes) -> None:
        fmt = self._get_format(filename)
        size_mb = self._get_size_mb(file_bytes)

        if fmt not in SUPPORTED_IMAGE_FORMATS:
            raise FileValidationError(
                f"Unsupported image format '{fmt}'. Only JPG, PNG, and WEBP are supported."
            )
        if size_mb > MAX_IMAGE_SIZE_MB:
            raise FileValidationError(
                f"Image size {size_mb:.1f}MB exceeds maximum of {MAX_IMAGE_SIZE_MB}MB."
            )

    def validate_audio(self, filename: str, file_bytes: bytes) -> None:
        fmt = self._get_format(filename)
        size_mb = self._get_size_mb(file_bytes)

        if fmt not in SUPPORTED_AUDIO_FORMATS:
            raise FileValidationError(
                f"Unsupported audio format '{fmt}'. Only MP3, WAV, OGG, M4A, and AAC are supported."
            )
        if size_mb > MAX_AUDIO_SIZE_MB:
            raise FileValidationError(
                f"Audio size {size_mb:.1f}MB exceeds maximum of {MAX_AUDIO_SIZE_MB}MB."
            )

    # ─────────────────────────────────────────
    # Upload (Cloudinary)
    # ─────────────────────────────────────────

    async def _upload_to_cloudinary(self, filename: str, file_bytes: bytes, resource_type: str) -> str:
        """
        Upload file bytes to Cloudinary and return public URL.
        resource_type: 'video' for video/audio, 'image' for images.
        Cloudinary treats audio as resource_type='video'.
        """
        with tempfile.NamedTemporaryFile(
            suffix=Path(filename).suffix,
            delete=False
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            def do_upload():
                result = cloudinary.uploader.upload(
                    tmp_path,
                    resource_type=resource_type,
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False,
                )
                return result["secure_url"]

            url = await asyncio.to_thread(do_upload)
            logger.info(f"✅ Uploaded to Cloudinary: {url}")
            return url

        except Exception as e:
            logger.error(f"❌ Cloudinary upload failed: {e}")
            raise
        finally:
            os.unlink(tmp_path)

    # ─────────────────────────────────────────
    # Public upload methods
    # ─────────────────────────────────────────

    async def upload_video(
        self,
        filename: str,
        file_bytes: bytes,
        placeholder: str = "@Video1"
    ) -> dict:
        """Validate and upload video to Cloudinary"""
        logger.info(f"Uploading video: {filename} ({self._get_size_mb(file_bytes):.1f}MB)")
        self.validate_video(filename, file_bytes)
        url = await self._upload_to_cloudinary(filename, file_bytes, resource_type="video")

        return {
            "placeholder": placeholder,
            "url": url,
            "format": self._get_format(filename).replace(".", ""),
            "size_mb": round(self._get_size_mb(file_bytes), 2),
        }

    async def upload_image(
        self,
        filename: str,
        file_bytes: bytes,
        placeholder: str = "@Image1"
    ) -> dict:
        """Validate and upload image to Cloudinary"""
        logger.info(f"Uploading image: {filename} ({self._get_size_mb(file_bytes):.1f}MB)")
        self.validate_image(filename, file_bytes)
        url = await self._upload_to_cloudinary(filename, file_bytes, resource_type="image")

        return {
            "placeholder": placeholder,
            "url": url,
            "format": self._get_format(filename).replace(".", ""),
            "size_mb": round(self._get_size_mb(file_bytes), 2),
        }

    async def upload_audio(
        self,
        filename: str,
        file_bytes: bytes,
        placeholder: str = "@Audio1"
    ) -> dict:
        """Validate and upload audio to Cloudinary.
        Note: Cloudinary uses resource_type='video' for audio files too.
        """
        logger.info(f"Uploading audio: {filename} ({self._get_size_mb(file_bytes):.1f}MB)")
        self.validate_audio(filename, file_bytes)
        url = await self._upload_to_cloudinary(filename, file_bytes, resource_type="video")

        return {
            "placeholder": placeholder,
            "url": url,
            "format": self._get_format(filename).replace(".", ""),
            "size_mb": round(self._get_size_mb(file_bytes), 2),
        }

    async def upload_multiple_images(
        self,
        files: list[tuple[str, bytes]]
    ) -> list[dict]:
        """Upload multiple images. Max 4."""
        if len(files) > 4:
            raise FileValidationError("Maximum 4 images allowed.")

        results = []
        for i, (filename, file_bytes) in enumerate(files, 1):
            result = await self.upload_image(
                filename=filename,
                file_bytes=file_bytes,
                placeholder=f"@Image{i}"
            )
            results.append(result)

        return results

    # ─────────────────────────────────────────
    # Video metadata
    # ─────────────────────────────────────────

    async def get_video_metadata_from_url(self, url: str) -> dict:
        """Get video metadata from URL using ffprobe."""
        import subprocess

        def run_ffprobe():
            duration_result = subprocess.run(
                ["ffprobe", "-v", "error",
                 "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", url],
                capture_output=True, text=True
            )
            size_result = subprocess.run(
                ["ffprobe", "-v", "error",
                 "-show_entries", "stream=width,height",
                 "-of", "default=noprint_wrappers=1:nokey=1", url],
                capture_output=True, text=True
            )
            duration = float(duration_result.stdout.strip() or 0)
            lines = size_result.stdout.strip().split("\n")
            width = int(lines[0]) if len(lines) > 0 and lines[0].strip() else 1920
            height = int(lines[1]) if len(lines) > 1 and lines[1].strip() else 1080
            return duration, width, height

        try:
            duration, width, height = await asyncio.to_thread(run_ffprobe)
        except Exception as e:
            logger.warning(f"ffprobe failed for URL, using defaults: {e}")
            duration, width, height = 0.0, 1920, 1080

        fmt = url.split(".")[-1].lower().split("?")[0] if "." in url else "mp4"

        return {
            "url": url,
            "format": fmt,
            "duration": duration,
            "size_mb": 0.0,
            "width": width,
            "height": height,
        }

    async def get_video_metadata(
        self,
        url: str,
        filename: str,
        file_bytes: bytes
    ) -> dict:
        """Build video metadata dict from file bytes."""
        fmt = self._get_format(filename).replace(".", "")
        size_mb = self._get_size_mb(file_bytes)
        duration, width, height = await self._get_video_info(file_bytes, filename)

        return {
            "url": url,
            "format": fmt,
            "duration": duration,
            "size_mb": round(size_mb, 2),
            "width": width,
            "height": height,
        }

    async def _get_video_info(
        self,
        file_bytes: bytes,
        filename: str
    ) -> tuple[float, int, int]:
        """Get video duration, width, height using ffprobe."""
        import subprocess

        with tempfile.NamedTemporaryFile(
            suffix=Path(filename).suffix,
            delete=False
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            def run_ffprobe():
                duration_result = subprocess.run(
                    ["ffprobe", "-v", "error",
                     "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", tmp_path],
                    capture_output=True, text=True
                )
                size_result = subprocess.run(
                    ["ffprobe", "-v", "error",
                     "-show_entries", "stream=width,height",
                     "-of", "default=noprint_wrappers=1:nokey=1", tmp_path],
                    capture_output=True, text=True
                )
                duration = float(duration_result.stdout.strip() or 0)
                lines = size_result.stdout.strip().split("\n")
                width = int(lines[0]) if len(lines) > 0 and lines[0].strip() else 1920
                height = int(lines[1]) if len(lines) > 1 and lines[1].strip() else 1080
                return duration, width, height

            return await asyncio.to_thread(run_ffprobe)

        except Exception as e:
            logger.warning(f"ffprobe failed, using defaults: {e}")
            return 0.0, 1920, 1080
        finally:
            os.unlink(tmp_path)