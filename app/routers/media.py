from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import MediaCreatedResponse
from app.services import media_service

router = APIRouter(prefix="/api/medias", tags=["Media"])


@router.post(
    "",
    response_model=MediaCreatedResponse,
    summary="Загрузить изображение",
)
async def upload_media(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaCreatedResponse:
    """Upload an image and return its ID for attachment to a tweet."""
    media = await media_service.save_media(
        db=db,
        file=file,
        owner_id=current_user.id,
    )
    return MediaCreatedResponse(media_id=media.id)
