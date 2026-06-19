from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.ai_chat import AiChatMessage, AiChatSession
from app.models.resume import Resume
from app.models.resume import ResumeVersion
from app.models.user import User
from app.schemas.ai_chat import AiChatMessageOut
from app.services.ai.chains import (
    localize_ai_text,
    resume_chat_action_reply_stream,
    resume_chat_chain,
    resume_chat_reply_stream,
)


CHANGE_REQUEST_WORDS = (
    "帮我改",
    "帮我写",
    "帮我删",
    "帮我优化",
    "帮我调整",
    "帮我补充",
    "帮我添加",
    "增加",
    "新增",
    "添加",
    "创建一个",
    "生成一个",
    "修改",
    "改写",
    "润色",
    "写入简历",
    "插入简历",
    "添加到简历",
    "从简历删除",
    "调整简历",
    "调到",
    "调整到",
    "移到",
    "移至",
    "移动到",
    "挪到",
    "放到",
    "放在",
    "放至",
    "提前",
    "后移",
    "上移",
    "下移",
    "置顶",
    "置后",
    "重新排序",
    "调整顺序",
    "更改顺序",
    "改变顺序",
    "模块顺序",
    "隐藏模块",
    "显示模块",
    "重命名模块",
    "修改标题",
    "优化个人简介",
    "优化项目",
    "优化经历",
)
CLARIFICATION_MARKERS = (
    "请告诉我",
    "请提供",
    "请补充",
    "需要你补充",
    "需要补充",
    "你希望我",
    "请确认",
    "等你补充",
    "等你回答",
)
GENERATION_AUTHORIZATION_WORDS = (
    "你来生成",
    "自己生成",
    "自行生成",
    "帮我生成",
    "帮我创建",
    "直接生成",
    "不用问我",
    "增加一个",
    "新增一个",
    "添加一个",
    "创建一个",
    "生成一个",
)
CONFIRM_WORDS = (
    "确认",
    "确认修改",
    "同意",
    "同意修改",
    "执行修改",
    "应用修改",
    "写入简历",
    "可以修改",
    "可以",
    "好的",
    "好",
    "行",
    "没问题",
    "就这样",
    "按这个修改",
)
REJECT_WORDS = ("取消", "取消修改", "不要修改", "不改了", "放弃修改")

SECTION_LABELS = {
    "basics": "基本信息",
    "summary": "个人简介",
    "education": "教育经历",
    "skills": "专业技能",
    "work": "实习/工作经历",
    "projects": "项目经历",
    "awards": "荣誉奖项",
}
SECTION_ALIASES = {
    "基本信息": "basics",
    "个人简介": "summary",
    "个人介绍": "summary",
    "教育经历": "education",
    "教育背景": "education",
    "专业技能": "skills",
    "技能特长": "skills",
    "实习经历": "work",
    "工作经历": "work",
    "实习/工作经历": "work",
    "项目经历": "projects",
    "荣誉奖项": "awards",
    "荣誉奖励": "awards",
    "获奖经历": "awards",
}


def _should_prepare_resume_changes(message: str, reply: str) -> bool:
    wants_change = any(word in message for word in CHANGE_REQUEST_WORDS)
    authorizes_generation = any(word in message for word in GENERATION_AUTHORIZATION_WORDS)
    asks_for_facts = any(marker in reply for marker in CLARIFICATION_MARKERS)
    return wants_change and (authorizes_generation or not asks_for_facts)


def _message_out(message: AiChatMessage) -> AiChatMessageOut:
    return AiChatMessageOut.model_validate(
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "suggestions": message.suggestions or [],
            "optimized_resume_data": message.optimized_resume_data,
            "action_status": message.action_status or "none",
            "create_time": message.create_time,
        }
    )


def get_or_create_chat_session(db: Session, user_id: int, resume_id: int) -> AiChatSession:
    session = db.scalar(
        select(AiChatSession)
        .where(AiChatSession.user_id == user_id, AiChatSession.resume_id == resume_id)
        .order_by(AiChatSession.id.asc())
    )
    if session:
        return session
    session = AiChatSession(user_id=user_id, resume_id=resume_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_chat_messages(db: Session, user_id: int, resume_id: int, limit: int = 80) -> list[AiChatMessageOut]:
    session = get_or_create_chat_session(db, user_id, resume_id)
    messages = list(
        db.scalars(
            select(AiChatMessage)
            .where(AiChatMessage.session_id == session.id, AiChatMessage.user_id == user_id)
            .order_by(AiChatMessage.id.desc())
            .limit(limit)
        )
    )
    return [_message_out(message) for message in reversed(messages)]


def clear_chat_messages(db: Session, user_id: int, resume_id: int) -> None:
    session = get_or_create_chat_session(db, user_id, resume_id)
    db.execute(delete(AiChatMessage).where(AiChatMessage.session_id == session.id, AiChatMessage.user_id == user_id))
    session.update_time = datetime.now()
    db.add(session)
    db.commit()


def _chat_context(db: Session, user: User, resume: Resume, content: str) -> tuple[AiChatSession, str, dict[str, Any]]:
    message = content.strip()
    if not message:
        raise AppException("请输入要咨询的问题")

    session = get_or_create_chat_session(db, user.id, resume.id)
    history = list_chat_messages(db, user.id, resume.id, limit=20)
    payload: dict[str, Any] = {
        "user": {"id": user.id, "username": user.username, "email": user.email},
        "resume": {
            "id": resume.id,
            "title": resume.title,
            "target_position": (resume.resume_data or {}).get("basics", {}).get("title", ""),
            "resume_data": resume.resume_data,
        },
        "history": [{"role": item.role, "content": item.content} for item in history[-12:]],
        "user_message": message,
    }
    return session, message, payload


def _save_assistant_message(
    db: Session,
    session: AiChatSession,
    user: User,
    resume: Resume,
    reply: str,
    suggestions: list[str],
    optimized_resume_data: dict[str, Any] | None,
) -> AiChatMessageOut:
    assistant_message = AiChatMessage(
        session_id=session.id,
        user_id=user.id,
        resume_id=resume.id,
        role="assistant",
        content=reply,
        suggestions=suggestions,
        optimized_resume_data=optimized_resume_data,
        action_status="pending" if optimized_resume_data else "none",
    )
    session.update_time = datetime.now()
    db.add(assistant_message)
    db.add(session)
    db.commit()
    db.refresh(assistant_message)
    return _message_out(assistant_message)


def _latest_pending_change(db: Session, user_id: int, resume_id: int) -> AiChatMessage | None:
    return db.scalar(
        select(AiChatMessage)
        .where(
            AiChatMessage.user_id == user_id,
            AiChatMessage.resume_id == resume_id,
            AiChatMessage.role == "assistant",
            AiChatMessage.action_status == "pending",
            AiChatMessage.optimized_resume_data.is_not(None),
        )
        .order_by(AiChatMessage.id.desc())
    )


def _decision_from_text(content: str) -> str | None:
    normalized = "".join(content.strip().split()).rstrip("。！!")
    if normalized in CONFIRM_WORDS:
        return "apply"
    if normalized in REJECT_WORDS:
        return "reject"
    return None


def _prepare_section_reorder(
    resume_data: dict[str, Any] | None,
    content: str,
) -> tuple[dict[str, Any], str, list[str]] | None:
    if any(marker in content for marker in ("是否", "该不该", "要不要", "应不应该", "怎么评价")):
        return None

    matches: list[tuple[int, str, str]] = []
    aliases = dict(SECTION_ALIASES)
    section_titles = (resume_data or {}).get("layout", {}).get("section_titles", {})
    if isinstance(section_titles, dict):
        for key, title in section_titles.items():
            if isinstance(title, str) and title.strip():
                aliases[title.strip()] = key

    for label, key in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
        position = content.find(label)
        if position >= 0 and not any(existing[1] == key for existing in matches):
            matches.append((position, key, label))
    matches.sort(key=lambda item: item[0])
    if not matches:
        return None

    target_index, target_key, target_label = matches[0]
    if target_key == "basics":
        return None

    layout = (resume_data or {}).get("layout", {})
    raw_order = layout.get("section_order", []) if isinstance(layout, dict) else []
    order = [key for key in raw_order if isinstance(key, str)]
    if target_key not in order:
        return None
    before_order = order.copy()
    order.remove(target_key)

    destination = next((match for match in matches[1:] if match[1] != target_key), None)
    relation_text = content[target_index:]
    if destination and destination[1] in order:
        destination_key = destination[1]
        destination_index = order.index(destination_key)
        destination_tail = content[destination[0] + len(destination[2]):]
        if any(word in destination_tail[:8] for word in ("后面", "之后", "下方")):
            insert_at = destination_index + 1
        else:
            insert_at = destination_index
    elif any(word in relation_text for word in ("最后", "末尾", "最下面", "最下方", "靠后")):
        insert_at = len(order)
    elif any(word in relation_text for word in ("最前", "前面", "最上面", "最上方", "靠前", "提前", "置顶")):
        insert_at = 1 if order and order[0] == "basics" else 0
    else:
        return None

    order.insert(insert_at, target_key)
    if order == before_order:
        return None

    optimized_data = deepcopy(resume_data or {})
    optimized_layout = optimized_data.setdefault("layout", {})
    optimized_layout["section_order"] = order

    def display_order(keys: list[str]) -> str:
        titles = section_titles if isinstance(section_titles, dict) else {}
        return " → ".join(str(titles.get(key) or SECTION_LABELS.get(key) or key) for key in keys)

    reply = (
        f"我准备调整 **{target_label}** 的位置。\n\n"
        f"**调整前：** {display_order(before_order)}\n\n"
        f"**调整后：** {display_order(order)}\n\n"
        "是否确认按这个顺序修改？"
    )
    return optimized_data, reply, [f"将{target_label}调整到新的模块位置"]


def _merge_confirmed_resume_data(
    current_data: dict[str, Any] | None,
    optimized_data: dict[str, Any],
) -> dict[str, Any]:
    """Apply the proposed content without dropping omitted resume configuration."""
    current = deepcopy(current_data or {})
    optimized = deepcopy(optimized_data)
    merged = {**current, **optimized}

    for key in ("basics", "layout"):
        current_section = current.get(key)
        optimized_section = optimized.get(key)
        if isinstance(current_section, dict) and isinstance(optimized_section, dict):
            merged[key] = {**current_section, **optimized_section}

    return merged


_NUMERIC_CLAIM_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?(?:%|\+)?")
_NUMERIC_SKIP_KEYS = {"id", "row", "order", "icon", "field_config", "layout"}


def _numeric_claims(value: Any, key: str | None = None) -> set[str]:
    """Collect user-visible numeric claims while ignoring structural configuration."""
    if key in _NUMERIC_SKIP_KEYS:
        return set()
    if isinstance(value, dict):
        claims: set[str] = set()
        for child_key, child_value in value.items():
            claims.update(_numeric_claims(child_value, str(child_key)))
        return claims
    if isinstance(value, list):
        claims: set[str] = set()
        for item in value:
            claims.update(_numeric_claims(item, key))
        return claims
    if isinstance(value, str):
        return set(_NUMERIC_CLAIM_RE.findall(value))
    return set()


def _unverified_numeric_claims(payload: dict[str, Any], optimized_data: dict[str, Any]) -> set[str]:
    source = {
        "resume_data": payload.get("resume", {}).get("resume_data") or {},
        "history": payload.get("history") or [],
        "user_message": payload.get("user_message") or "",
    }
    return _numeric_claims(optimized_data) - _numeric_claims(source)


def _validated_optimized_data(
    payload: dict[str, Any],
    current_data: dict[str, Any] | None,
    optimized_data: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str]:
    if not optimized_data:
        return None, ""

    merged = _merge_confirmed_resume_data(current_data, optimized_data)
    if merged == (current_data or {}):
        return None, "模型没有生成实际内容变化，未创建待确认修改。"
    if _unverified_numeric_claims(payload, merged):
        return None, "检测到方案包含简历和对话中未提供的量化结果，已阻止写入。"
    return merged, ""


def resolve_chat_change(
    db: Session,
    user: User,
    resume: Resume,
    message_id: int,
    action: str,
) -> tuple[AiChatMessageOut, dict[str, Any] | None]:
    message = db.get(AiChatMessage, message_id)
    if (
        not message
        or message.user_id != user.id
        or message.resume_id != resume.id
        or message.role != "assistant"
    ):
        raise AppException("待确认修改不存在", 404)
    if message.action_status != "pending":
        raise AppException("这次修改已经处理过了", 409)

    resume_data: dict[str, Any] | None = None
    if action == "apply":
        if not message.optimized_resume_data:
            raise AppException("这次对话没有可写入的修改")
        db.add(
            ResumeVersion(
                resume_id=resume.id,
                resume_data=deepcopy(resume.resume_data),
                template_config=deepcopy(resume.template_config),
                reason="采纳 AI 助手修改",
            )
        )
        resume.resume_data = _merge_confirmed_resume_data(
            resume.resume_data,
            message.optimized_resume_data,
        )
        resume.update_by = user.id
        message.action_status = "applied"
        resume_data = resume.resume_data
        db.add(resume)
    elif action == "reject":
        message.action_status = "rejected"
    else:
        raise AppException("不支持的确认操作", 400)

    db.add(message)
    db.commit()
    db.refresh(message)
    return _message_out(message), resume_data


def send_chat_message(db: Session, user: User, resume: Resume, content: str) -> tuple[list[AiChatMessageOut], AiChatMessageOut]:
    session, message, payload = _chat_context(db, user, resume, content)

    result = resume_chat_chain(payload)
    reorder_change = _prepare_section_reorder(resume.resume_data, message)
    if reorder_change:
        result.optimized_resume_data, _, result.suggestions = reorder_change
    optimized_data, validation_issue = _validated_optimized_data(
        payload,
        resume.resume_data,
        result.optimized_resume_data,
    )
    suggestions = result.suggestions if optimized_data else []
    reply = localize_ai_text(result.reply)
    if validation_issue:
        reply = (
            "当前信息不足以支持新增量化成果。请提供真实指标，"
            "或者我可以只优化现有内容的表达，不添加未经确认的数据。"
        )
    user_message = AiChatMessage(
        session_id=session.id,
        user_id=user.id,
        resume_id=resume.id,
        role="user",
        content=message,
        suggestions=[],
        optimized_resume_data=None,
    )
    db.add(user_message)
    db.commit()
    assistant_message = _save_assistant_message(
        db, session, user, resume, reply, suggestions, optimized_data
    )
    return list_chat_messages(db, user.id, resume.id), assistant_message


def stream_chat_message(db: Session, user: User, resume: Resume, content: str):
    session, message, payload = _chat_context(db, user, resume, content)
    decision = _decision_from_text(message)
    pending_change = _latest_pending_change(db, user.id, resume.id) if decision else None
    user_message = AiChatMessage(
        session_id=session.id,
        user_id=user.id,
        resume_id=resume.id,
        role="user",
        content=message,
        suggestions=[],
        optimized_resume_data=None,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    yield {"type": "start", "data": {"user_message_id": user_message.id}}
    if decision and pending_change:
        assistant_message, resume_data = resolve_chat_change(db, user, resume, pending_change.id, decision)
        action_result = {
            "status": "applied" if decision == "apply" else "rejected",
            "message": "修改已经写入简历" if decision == "apply" else "本次修改已取消",
            "suggestions": assistant_message.suggestions,
        }
        reply_chunks: list[str] = []
        try:
            for text in resume_chat_action_reply_stream({"action_result": action_result}):
                reply_chunks.append(text)
                yield {"type": "delta", "text": text}
            reply = localize_ai_text("".join(reply_chunks).strip())
            if not reply:
                reply = "修改已经写入简历。" if decision == "apply" else "本次修改已取消。"
                yield {"type": "delta", "text": reply}
        except Exception:
            reply = "修改已经写入简历。" if decision == "apply" else "本次修改已取消。"
            yield {"type": "delta", "text": reply}
        confirmation = _save_assistant_message(db, session, user, resume, reply, [], None)
        yield {
            "type": "result",
            "data": {
                "assistant_message": confirmation.model_dump(mode="json"),
                "resolved_message": assistant_message.model_dump(mode="json"),
                "resume_data": resume_data,
            },
        }
        return
    if decision:
        action_result = {
            "status": "no_pending",
            "message": "当前没有待确认、可写入简历的修改",
        }
        reply_chunks: list[str] = []
        try:
            for text in resume_chat_action_reply_stream({"action_result": action_result}):
                reply_chunks.append(text)
                yield {"type": "delta", "text": text}
            reply = localize_ai_text("".join(reply_chunks).strip())
            if not reply:
                reply = "当前没有待确认的修改，请重新告诉我要调整哪部分。"
                yield {"type": "delta", "text": reply}
        except Exception:
            reply = "当前没有待确认的修改，请重新告诉我要调整哪部分。"
            yield {"type": "delta", "text": reply}
        assistant_message = _save_assistant_message(db, session, user, resume, reply, [], None)
        yield {"type": "result", "data": {"assistant_message": assistant_message.model_dump(mode="json")}}
        return

    try:
        # Generate the authoritative structured result first. The visible reply is
        # written from that result, so the assistant cannot claim an unapplied change.
        yield {"type": "phase", "phase": "preparing_changes", "text": "正在分析简历和你的要求"}
        structured_result = resume_chat_chain(payload)
        reorder_change = _prepare_section_reorder(resume.resume_data, message)
        if reorder_change:
            optimized_data, _, suggestions = reorder_change
            structured_result.optimized_resume_data = optimized_data
            structured_result.suggestions = suggestions

        optimized_data, validation_issue = _validated_optimized_data(
            payload,
            resume.resume_data,
            structured_result.optimized_resume_data,
        )
        suggestions = structured_result.suggestions if optimized_data else []
        draft_reply = localize_ai_text(structured_result.reply)
        if validation_issue:
            draft_reply = (
                "当前信息不足以支持新增量化成果。请提供真实指标，"
                "或者我可以只优化现有内容的表达，不添加未经确认的数据。"
            )

        reply_payload = deepcopy(payload)
        reply_payload["prepared_result"] = {
            "has_changes": bool(optimized_data),
            "draft_reply": draft_reply,
            "suggestions": suggestions,
            "validation_issue": validation_issue,
        }
        yield {"type": "phase", "phase": "replying", "text": "正在组织回复"}
        reply_chunks: list[str] = []
        try:
            for text in resume_chat_reply_stream(reply_payload):
                reply_chunks.append(text)
                yield {"type": "delta", "text": text}
            reply = localize_ai_text("".join(reply_chunks).strip())
        except Exception:
            reply = draft_reply
            yield {"type": "delta", "text": reply}
        if not reply:
            reply = draft_reply or "我已经看过当前简历，请告诉我你想重点调整的内容。"
            yield {"type": "delta", "text": reply}

        assistant_message = _save_assistant_message(
            db,
            session,
            user,
            resume,
            reply,
            suggestions,
            optimized_data,
        )
        yield {"type": "result", "data": {"assistant_message": assistant_message.model_dump(mode="json")}}
    except AppException as exc:
        yield {"type": "error", "message": exc.message}
    except Exception as exc:
        raw_message = str(exc) or "AI 对话失败"
        message_text = "AI 服务连接失败，请检查模型配置或网络连通性" if "connection" in raw_message.lower() else raw_message
        yield {"type": "error", "message": message_text}
