from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeCreate, ResumeOut, ResumeUpdate, ResumeVersionCreate
from app.services.preview_service import render_resume_html
from app.services.pdf_export_service import get_pdf_path
from app.services.resume_service import (
    create_resume,
    create_version,
    delete_resume,
    duplicate_resume,
    get_resume,
    list_resumes,
    update_resume,
)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("")
def list_my_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success([ResumeOut.model_validate(item).model_dump() for item in list_resumes(db, current_user.id)])


@router.post("")
def create(payload: ResumeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(ResumeOut.model_validate(create_resume(db, current_user.id, payload)).model_dump())


@router.get("/{resume_id}")
def detail(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(ResumeOut.model_validate(get_resume(db, current_user.id, resume_id)).model_dump())


@router.put("/{resume_id}")
def update(resume_id: int, payload: ResumeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(ResumeOut.model_validate(update_resume(db, current_user.id, resume_id, payload)).model_dump())


@router.delete("/{resume_id}")
def remove(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_resume(db, current_user.id, resume_id)
    return success(True)


@router.post("/{resume_id}/duplicate")
def duplicate(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(ResumeOut.model_validate(duplicate_resume(db, current_user.id, resume_id)).model_dump())


@router.post("/{resume_id}/versions")
def version(resume_id: int, payload: ResumeVersionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = create_version(db, current_user.id, resume_id, payload.reason)
    return success({"id": item.id})


@router.get("/{resume_id}/preview-html", response_class=HTMLResponse)
def preview_html(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = get_resume(db, current_user.id, resume_id)
    html = render_resume_html(resume.resume_data, resume.template_id, resume.template_config)
    return HTMLResponse(content=html, headers={"Cache-Control": "no-store"})


@router.get("/{resume_id}/preview-pdf")
def preview_pdf(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = get_resume(db, current_user.id, resume_id)
    path = get_pdf_path(resume)
    return FileResponse(path, media_type="application/pdf", headers={"Cache-Control": "no-store"})
