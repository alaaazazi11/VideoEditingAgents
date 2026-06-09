import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional
from api.services.file_service import FileService, FileValidationError
from api.models.responses import UploadResponse

logger = logging.getLogger("upload_router")
router = APIRouter(prefix="/upload", tags=["Upload"])
file_service = FileService()


# ─────────────────────────────────────────
# Video
# ─────────────────────────────────────────

@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    placeholder: str = Query(default="@Video1")
):
    """
    Upload a video file to fal.ai storage.
    Supported formats: MP4, MOV
    Max size: 200MB
    """
    try:
        logger.info(f"📤 Uploading video: {file.filename}")
        file_bytes = await file.read()

        result = await file_service.upload_video(
            filename=file.filename,
            file_bytes=file_bytes,
            placeholder=placeholder
        )

        return UploadResponse(**result)

    except FileValidationError as e:
        logger.warning(f"❌ Video validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Video upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload video. Please try again.")


# ─────────────────────────────────────────
# Image
# ─────────────────────────────────────────

@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    placeholder: str = Query(default="@Image1")
):
    """
    Upload a single image file to fal.ai storage.
    Supported formats: JPG, PNG, WEBP
    Max size: 10MB
    """
    try:
        logger.info(f"📤 Uploading image: {file.filename}")
        file_bytes = await file.read()

        result = await file_service.upload_image(
            filename=file.filename,
            file_bytes=file_bytes,
            placeholder=placeholder
        )

        return UploadResponse(**result)

    except FileValidationError as e:
        logger.warning(f"❌ Image validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Image upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image. Please try again.")


@router.post("/images", response_model=list[UploadResponse])
async def upload_multiple_images(
    files: list[UploadFile] = File(...),
):
    """
    Upload multiple images at once.
    Auto-assigns @Image1, @Image2, etc.
    Max 4 images.
    """
    if len(files) > 4:
        raise HTTPException(
            status_code=400,
            detail="Maximum 4 images allowed."
        )

    results = []
    for i, file in enumerate(files, 1):
        try:
            logger.info(f"📤 Uploading image {i}: {file.filename}")
            file_bytes = await file.read()

            result = await file_service.upload_image(
                filename=file.filename,
                file_bytes=file_bytes,
                placeholder=f"@Image{i}"
            )
            results.append(UploadResponse(**result))

        except FileValidationError as e:
            logger.warning(f"❌ Image {i} validation failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Image {i} ({file.filename}): {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Image {i} upload failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image {i}. Please try again."
            )

    return results


# ─────────────────────────────────────────
# Audio
# ─────────────────────────────────────────

@router.post("/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    placeholder: str = Query(default="@Audio1")
):
    """
    Upload an audio file to fal.ai storage.
    Supported formats: MP3, WAV, OGG, M4A, AAC
    Max size: 50MB
    """
    try:
        logger.info(f"📤 Uploading audio: {file.filename}")
        file_bytes = await file.read()

        result = await file_service.upload_audio(
            filename=file.filename,
            file_bytes=file_bytes,
            placeholder=placeholder
        )

        return UploadResponse(**result)

    except FileValidationError as e:
        logger.warning(f"❌ Audio validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload audio. Please try again.")