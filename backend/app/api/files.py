from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.response import success
from app.core.security import get_current_user
from app.models.user import User
from app.services.storage.storage_service import stream_uploaded_file, upload_avatar

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload-avatar")
def upload_avatar_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success(upload_avatar(db, current_user.id, file))


@router.get("/font-assets/{file_name}")
def get_font_asset(file_name: str):
    safe_name = file_name.rsplit("/", 1)[-1]
    file_path = settings.backend_root / "app" / "static" / "fonts" / safe_name
    if safe_name != file_name or not file_path.is_file():
        raise HTTPException(status_code=404, detail="字体文件不存在")
    return FileResponse(file_path, media_type="font/woff2")


@router.get("/{object_name:path}")
def get_uploaded_file(object_name: str):
    return stream_uploaded_file(object_name)
