from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.response import success
from app.core.security import create_access_token, get_current_user, get_password_hash, verify_password
from app.models.user import EmailVerificationCode, User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    SendVerificationCodeRequest,
    TokenOut,
    UpdateProfileRequest,
    UserOut,
)
from app.services.email_service import send_registration_code

router = APIRouter(prefix="/auth", tags=["auth"])


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


@router.post("/verification-code")
def send_verification_code(payload: SendVerificationCodeRequest, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    if db.scalar(select(User.id).where(func.lower(User.email) == email)):
        raise AppException("该邮箱已注册")

    latest = db.scalar(
        select(EmailVerificationCode)
        .where(EmailVerificationCode.email == email, EmailVerificationCode.purpose == "register")
        .order_by(EmailVerificationCode.create_time.desc())
    )
    now = datetime.now()
    if latest and (now - latest.create_time).total_seconds() < settings.email_code_send_interval_seconds:
        raise AppException(f"请在 {settings.email_code_send_interval_seconds} 秒后重新发送")

    code = f"{secrets.randbelow(1_000_000):06d}"
    send_registration_code(email, code)
    db.add(
        EmailVerificationCode(
            email=email,
            code_hash=hash_code(code),
            purpose="register",
            expires_at=now + timedelta(minutes=settings.email_code_expire_minutes),
        )
    )
    db.commit()
    return success(message="验证码已发送")


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    if db.scalar(select(User).where(User.username == payload.username)):
        raise AppException("用户名已存在")
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise AppException("邮箱已存在")

    verification = db.scalar(
        select(EmailVerificationCode)
        .where(
            EmailVerificationCode.email == email,
            EmailVerificationCode.purpose == "register",
            EmailVerificationCode.used.is_(False),
        )
        .order_by(EmailVerificationCode.create_time.desc())
    )
    if not verification or verification.expires_at < datetime.now():
        raise AppException("验证码无效或已过期，请重新获取")
    if not hmac.compare_digest(verification.code_hash, hash_code(payload.verification_code)):
        raise AppException("验证码错误")

    verification.used = True
    user = User(username=payload.username.strip(), email=email, password_hash=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return success(UserOut.model_validate(user).model_dump())


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(func.lower(User.email) == normalize_email(payload.email)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppException("邮箱或密码错误")
    token = create_access_token(user.id)
    return success(TokenOut(access_token=token, user=UserOut.model_validate(user)).model_dump())


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user).model_dump())


@router.put("/profile")
def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username = payload.username.strip()
    exists = db.scalar(select(User.id).where(User.username == username, User.id != current_user.id))
    if exists:
        raise AppException("用户名已存在")
    current_user.username = username
    db.commit()
    db.refresh(current_user)
    return success(UserOut.model_validate(current_user).model_dump(), "用户名已更新")


@router.put("/password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise AppException("当前密码错误")
    if payload.current_password == payload.new_password:
        raise AppException("新密码不能与当前密码相同")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return success(message="密码已修改")
