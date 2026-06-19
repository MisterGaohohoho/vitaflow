from fastapi import APIRouter

from app.core.exceptions import AppException
from app.core.response import success
from app.services.template_service import get_template, list_templates

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
def templates():
    return success(list_templates())


@router.get("/{template_id}")
def template_detail(template_id: str):
    template = get_template(template_id)
    if not template:
        raise AppException("模板不存在")
    return success(template)
