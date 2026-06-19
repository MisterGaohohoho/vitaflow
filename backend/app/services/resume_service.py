from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.resume import Resume, ResumeVersion
from app.schemas.resume import ResumeCreate, ResumeUpdate, default_template_config


def list_resumes(db: Session, user_id: int) -> list[Resume]:
    return list(db.scalars(select(Resume).where(Resume.user_id == user_id).order_by(Resume.update_time.desc())))


def get_resume(db: Session, user_id: int, resume_id: int) -> Resume:
    resume = db.get(Resume, resume_id)
    if not resume or resume.user_id != user_id:
        raise AppException("简历不存在")
    return resume


def create_resume(db: Session, user_id: int, payload: ResumeCreate) -> Resume:
    config = payload.template_config or default_template_config(payload.template_id)
    config["template_id"] = payload.template_id
    resume = Resume(
        user_id=user_id,
        title=payload.title,
        language=payload.language,
        resume_data=payload.resume_data,
        template_id=payload.template_id,
        template_config=config,
        create_by=user_id,
        update_by=user_id,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def update_resume(db: Session, user_id: int, resume_id: int, payload: ResumeUpdate) -> Resume:
    resume = get_resume(db, user_id, resume_id)
    data = payload.model_dump(exclude_unset=True)
    if "template_id" in data and data["template_id"]:
        data.setdefault("template_config", resume.template_config or {})
        data["template_config"]["template_id"] = data["template_id"]
    for key, value in data.items():
        setattr(resume, key, value)
    resume.update_by = user_id
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def delete_resume(db: Session, user_id: int, resume_id: int) -> None:
    resume = get_resume(db, user_id, resume_id)
    db.delete(resume)
    db.commit()


def duplicate_resume(db: Session, user_id: int, resume_id: int) -> Resume:
    source = get_resume(db, user_id, resume_id)
    copy = Resume(
        user_id=user_id,
        title=f"{source.title} 副本",
        language=source.language,
        resume_data=source.resume_data,
        template_id=source.template_id,
        template_config=source.template_config,
        create_by=user_id,
        update_by=user_id,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


def create_version(db: Session, user_id: int, resume_id: int, reason: str) -> ResumeVersion:
    resume = get_resume(db, user_id, resume_id)
    version = ResumeVersion(
        resume_id=resume.id,
        resume_data=resume.resume_data,
        template_config=resume.template_config,
        reason=reason,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
