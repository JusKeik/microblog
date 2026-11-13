"""Services for uploading and validating media files."""

import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import ConflictError
from app.models import Media

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
}


def _detect_extension(content: bytes) -> str | None:
    """Detect an image type by its binary signature."""
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp"
    for signature, extension in IMAGE_SIGNATURES.items():
        if content.startswith(signature):
            return extension
    return None


async def save_media(
    db: Session,
    file: UploadFile,
    owner_id: int,
) -> Media:
    """Validate, store and register an uploaded image."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ConflictError("Поддерживаются только JPEG, PNG и WebP")

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise ConflictError("Файл пустой")

    if len(content) > MAX_FILE_SIZE:
        raise ConflictError("Максимальный размер файла — 5 МБ")

    detected_extension = _detect_extension(content)

    if detected_extension != ALLOWED_CONTENT_TYPES[file.content_type]:
        raise ConflictError("Файл не является поддерживаемым изображением")

    settings = get_settings()
    directory = Path(settings.media_directory)
    directory.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{detected_extension}"
    path = directory / filename

    try:
        path.write_bytes(content)
        media = Media(
            file_path=f"/static/media/{filename}",
            owner_id=owner_id,
        )
        db.add(media)
        db.commit()
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise

    db.refresh(media)
    return media
