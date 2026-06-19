import json
from collections.abc import Iterable
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.ai import (
    GenerateResumeRequest,
    JdOptimizeRequest,
    OptimizeResumeRequest,
    OptimizeSectionRequest,
    ProjectOptimizeRequest,
    ScoreResumeRequest,
    SummaryGenerateRequest,
)
from app.schemas.ai_chat import AiChatDecisionRequest, AiChatDecisionResponse, AiChatSendRequest, AiChatSendResponse
from app.services.ai.chains import (
    generate_resume_chain,
    generate_resume_stream,
    generate_summary_chain,
    optimize_by_jd_chain,
    optimize_by_jd_stream,
    optimize_project_chain,
    optimize_resume_chain,
    optimize_section_chain,
    optimize_section_stream,
    score_resume_chain,
    score_resume_stream,
)
from app.services.ai.graphs import optimize_by_jd_graph
from app.services.ai_chat_service import (
    clear_chat_messages,
    list_chat_messages,
    resolve_chat_change,
    send_chat_message,
    stream_chat_message,
)
from app.services.resume_service import get_resume

router = APIRouter(prefix="/ai", tags=["ai"])


def stream_events(events: Iterable[dict[str, Any]]) -> StreamingResponse:
    def iterator():
        for event in events:
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(
        iterator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/generate-resume")
def generate_resume(payload: GenerateResumeRequest, _: User = Depends(get_current_user)):
    return success(generate_resume_chain(payload.model_dump()).model_dump())


@router.post("/generate-resume/stream")
def generate_resume_stream_api(payload: GenerateResumeRequest, _: User = Depends(get_current_user)):
    return stream_events(generate_resume_stream(payload.model_dump()))


@router.post("/score-resume")
def score_resume(payload: ScoreResumeRequest, _: User = Depends(get_current_user)):
    return success(score_resume_chain(payload.model_dump()).model_dump())


@router.post("/score-resume/stream")
def score_resume_stream_api(payload: ScoreResumeRequest, _: User = Depends(get_current_user)):
    return stream_events(score_resume_stream(payload.model_dump()))


@router.post("/optimize-section")
def optimize_section(payload: OptimizeSectionRequest, _: User = Depends(get_current_user)):
    return success(optimize_section_chain(payload.model_dump()).model_dump())


@router.post("/optimize-section/stream")
def optimize_section_stream_api(payload: OptimizeSectionRequest, _: User = Depends(get_current_user)):
    return stream_events(optimize_section_stream(payload.model_dump()))


@router.post("/optimize-resume")
def optimize_resume(payload: OptimizeResumeRequest, _: User = Depends(get_current_user)):
    return success(optimize_resume_chain(payload.model_dump()).model_dump())


@router.post("/optimize-by-jd")
def optimize_by_jd(payload: JdOptimizeRequest, _: User = Depends(get_current_user)):
    return success(optimize_by_jd_graph(payload.resume_data, payload.job_description).model_dump())


@router.post("/optimize-by-jd/stream")
def optimize_by_jd_stream_api(payload: JdOptimizeRequest, _: User = Depends(get_current_user)):
    return stream_events(optimize_by_jd_stream(payload.model_dump()))


@router.post("/optimize-by-jd-single")
def optimize_by_jd_single(payload: JdOptimizeRequest, _: User = Depends(get_current_user)):
    return success(optimize_by_jd_chain(payload.model_dump()).model_dump())


@router.post("/generate-summary")
def generate_summary(payload: SummaryGenerateRequest, _: User = Depends(get_current_user)):
    return success(generate_summary_chain(payload.model_dump()).model_dump())


@router.post("/optimize-project")
def optimize_project(payload: ProjectOptimizeRequest, _: User = Depends(get_current_user)):
    return success(optimize_project_chain(payload.model_dump()).model_dump())


@router.get("/resume-chat/{resume_id}/messages")
def resume_chat_messages(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_resume(db, current_user.id, resume_id)
    return success([item.model_dump() for item in list_chat_messages(db, current_user.id, resume_id)])


@router.post("/resume-chat/{resume_id}/messages")
def resume_chat_send(
    resume_id: int,
    payload: AiChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = get_resume(db, current_user.id, resume_id)
    messages, assistant_message = send_chat_message(db, current_user, resume, payload.content)
    return success(
        AiChatSendResponse(messages=messages, assistant_message=assistant_message).model_dump()
    )


@router.post("/resume-chat/{resume_id}/messages/stream")
def resume_chat_send_stream(
    resume_id: int,
    payload: AiChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = get_resume(db, current_user.id, resume_id)
    return stream_events(stream_chat_message(db, current_user, resume, payload.content))


@router.post("/resume-chat/{resume_id}/messages/{message_id}/decision")
def resume_chat_decision(
    resume_id: int,
    message_id: int,
    payload: AiChatDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = get_resume(db, current_user.id, resume_id)
    assistant_message, resume_data = resolve_chat_change(
        db, current_user, resume, message_id, payload.action
    )
    return success(
        AiChatDecisionResponse(
            assistant_message=assistant_message,
            resume_data=resume_data,
        ).model_dump()
    )


@router.delete("/resume-chat/{resume_id}/messages")
def resume_chat_clear(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_resume(db, current_user.id, resume_id)
    clear_chat_messages(db, current_user.id, resume_id)
    return success(True)
