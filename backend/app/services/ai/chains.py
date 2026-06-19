import json
import re
from typing import Any, Optional, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.exceptions import AppException
from app.services.ai.llm import get_llm
from app.services.ai.prompts import (
    CHAT_ACTION_REPLY_PROMPT,
    GENERATE_RESUME_PROMPT,
    CHAT_RESUME_REPLY_PROMPT,
    CHAT_RESUME_PROMPT,
    JD_OPTIMIZE_PROMPT,
    JSON_REPAIR_PROMPT,
    OPTIMIZE_RESUME_PROMPT,
    OPTIMIZE_SECTION_PROMPT,
    PROJECT_PROMPT,
    SCORE_RESUME_PROMPT,
    SUMMARY_PROMPT,
)
from app.services.ai.schemas import (
    ProjectOptimizeResult,
    JdOptimizeResult,
    ResumeGenerateResult,
    ResumeChatResult,
    ResumeOptimizeResult,
    ResumeScoreResult,
    SectionOptimizeResult,
    SummaryGenerateResult,
)

T = TypeVar("T", bound=BaseModel)

BUILT_IN_SECTIONS = ["basics", "summary", "education", "skills", "work", "projects", "awards"]
BUILT_IN_TITLES = {
    "basics": "基本信息",
    "summary": "个人简介",
    "education": "教育经历",
    "skills": "专业技能",
    "work": "工作经历",
    "projects": "项目经历",
    "awards": "荣誉奖项",
}
DEFAULT_FIELD_CONFIG = {
    "phone": {"label": "电话", "icon": "Phone", "row": 1, "order": 1},
    "email": {"label": "邮箱", "icon": "Mail", "row": 1, "order": 2},
    "status": {"label": "当前状态", "icon": "Info", "row": 1, "order": 3},
    "location": {"label": "地点", "icon": "MapPin", "row": 1, "order": 4},
    "highest_degree": {"label": "最高学历", "icon": "GraduationCap", "row": 2, "order": 1},
    "website": {"label": "个人网站", "icon": "Globe", "row": 2, "order": 2},
    "github": {"label": "代码仓库", "icon": "Github", "row": 2, "order": 3},
    "expected_salary": {"label": "期望薪资", "icon": "Briefcase", "row": 2, "order": 4},
}


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",(\s*[}\]])", r"\1", text)


def _decode_json_candidate(text: str) -> Any:
    decoder = json.JSONDecoder()
    last_error: Optional[json.JSONDecodeError] = None
    candidates = [_strip_json_fence(text)]
    for opener in ("{", "["):
        index = text.find(opener)
        if index >= 0:
            candidate = text[index:]
            if candidate not in candidates:
                candidates.append(candidate)
    for candidate in candidates:
        for cleaned in (candidate, _remove_trailing_commas(candidate)):
            cleaned = _strip_json_fence(cleaned)
            if not cleaned:
                continue
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as exc:
                last_error = exc
            try:
                data, _ = decoder.raw_decode(cleaned)
                return data
            except json.JSONDecodeError as exc:
                last_error = exc
    if last_error:
        raise AppException(f"AI 输出不是合法 JSON，请重试：{last_error.msg}")
    raise AppException("AI 输出不是合法 JSON，请重试")


def _parse_json_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        data = content
    else:
        text = _strip_json_fence(str(content))
        data = _decode_json_candidate(text)
    if not isinstance(data, dict):
        raise AppException("AI 输出 JSON 顶层必须是对象")
    return data


def _repair_json_content(content: Any, task: str) -> dict[str, Any]:
    repair_chain = JSON_REPAIR_PROMPT | get_llm()
    repaired = repair_chain.invoke({"task": task, "raw_content": str(content)[:12000]})
    try:
        return _parse_json_content(getattr(repaired, "content", repaired))
    except AppException as exc:
        raise AppException(f"AI 输出 JSON 修复失败：{exc.message}") from exc


def _stringify_summary(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if isinstance(value.get("content"), str):
            return value["content"]
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return str(value)


def _safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        number = float(value)
        if 0 < number <= 1:
            number *= 100
        return int(round(number))
    if isinstance(value, str):
        match = re.search(r"\d+(?:\.\d+)?", value)
        if match:
            number = float(match.group(0))
            if 0 < number <= 1:
                number *= 100
            return int(round(number))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    if isinstance(value, dict):
        items: list[str] = []
        for key, item in value.items():
            if isinstance(item, list):
                items.extend(str(entry) for entry in item if entry is not None and str(entry).strip())
            elif item is not None and str(item).strip():
                items.append(f"{key}：{item}")
        return items
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _clean_score_text(value: Any) -> Any:
    if isinstance(value, str):
        result = value
        noisy_patterns = [
            r"简历评价[^\n。；;]*[。；;]?",
            r"简历内容本身[^\n。；;]*[。；;]?",
            r"简历使用\s*JSON\s*格式[，,、。；;\s]*",
            r"JSON\s*格式[，,、。；;\s]*",
            r"JSON\s*格式[^\n。；;]*[。；;]?",
            r"字段命名规范[，,、。；;\s]*",
            r"字段命名[^\n。；;]*[。；;]?",
            r"内部字段[^\n。；;]*[。；;]?",
            r"数据结构[^\n。；;]*[。；;]?",
            r"schema[^\n。；;]*[。；;]?",
        ]
        for pattern in noisy_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        return result.strip(" ，,。；;\n")
    if isinstance(value, list):
        return [_clean_score_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_score_text(item) for key, item in value.items()}
    return value


FIELD_LABELS = {
    "basics": "基本信息",
    "summary": "个人简介",
    "education": "教育经历",
    "skills": "专业技能",
    "work": "工作经历",
    "projects": "项目经历",
    "awards": "荣誉奖项",
    "name": "姓名",
    "title": "求职方向",
    "status": "当前状态",
    "phone": "电话",
    "email": "邮箱",
    "location": "所在城市",
    "expected_salary": "期望薪资",
    "highest_degree": "最高学历",
    "website": "个人网站",
    "github": "代码仓库",
    "school": "学校",
    "major": "专业",
    "degree": "学历",
    "start_date": "开始时间",
    "end_date": "结束时间",
    "description": "描述",
    "highlights": "亮点",
    "keywords": "关键词",
    "tech_stack": "技术栈",
    "field_config": "基本信息展示配置",
    "highlight": "亮点",
    "content": "内容",
    "resume_data": "简历内容",
    "optimized_resume_data": "优化后的简历内容",
}


def _localize_field_names(value: Any) -> Any:
    if isinstance(value, str):
        result = value
        for key, label in sorted(FIELD_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
            result = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(key)}(?![A-Za-z0-9_])", label, result)
        return result
    if isinstance(value, list):
        return [_localize_field_names(item) for item in value]
    if isinstance(value, dict):
        return {key: _localize_field_names(item) for key, item in value.items()}
    return value


def localize_ai_text(value: str) -> str:
    result = value
    user_hidden_fields = {
        "optimized_resume_data": "优化后的简历内容",
        "resume_data": "简历内容",
        "field_config": "基本信息展示配置",
        "highest_degree": "最高学历",
        "start_date": "开始时间",
        "end_date": "结束时间",
        "tech_stack": "技术栈",
        "description": "描述",
        "highlights": "亮点",
        "highlight": "亮点",
        "keywords": "关键词",
        "basics": "基本信息",
        "summary": "个人简介",
        "skills": "专业技能",
        "projects": "项目经历",
    }
    for key, label in sorted(user_hidden_fields.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(key)}(?![A-Za-z0-9_])", label, result, flags=re.IGNORECASE)
    return result


def _normalize_score_detail(value: Any, fallback_dimension: str = "评分维度") -> dict[str, Any]:
    if not isinstance(value, dict):
        score = _safe_int(value, 0)
        comment = "" if score else str(value)
        return {"dimension": fallback_dimension, "score": max(0, min(score, 100)), "max_score": 100, "comment": _clean_score_text(_localize_field_names(comment))}
    comment = (
        value.get("comment")
        or value.get("suggestion")
        or value.get("advice")
        or value.get("reason")
        or value.get("analysis")
        or value.get("feedback")
        or value.get("description")
        or value.get("问题")
        or value.get("建议")
        or ""
    )
    score = _safe_int(value.get("score", value.get("得分", value.get("points", value.get("value", 0)))), 0)
    max_score = _safe_int(value.get("max_score", value.get("max", value.get("满分", value.get("total", 100)))), 100) or 100
    if max_score != 100 and max_score > 0:
        score = int(round(score / max_score * 100))
        max_score = 100
    score = max(0, min(score, max_score))
    return {
        "dimension": _localize_field_names(str(value.get("dimension") or value.get("name") or fallback_dimension)),
        "score": score,
        "max_score": max_score,
        "comment": _clean_score_text(_localize_field_names(_stringify_summary(comment))),
    }


def _looks_like_resume_data(data: dict[str, Any]) -> bool:
    return "basics" in data and "layout" in data


def _extract_labeled_facts(text: str) -> dict[str, str]:
    facts: dict[str, str] = {}
    if not text:
        return facts
    aliases = {
        "姓名": "name",
        "名字": "name",
        "电话": "phone",
        "手机号": "phone",
        "手机": "phone",
        "邮箱": "email",
        "邮件": "email",
        "当前状态": "status",
        "状态": "status",
        "所在地": "location",
        "城市": "location",
        "地点": "location",
        "学校": "school",
        "院校": "school",
        "毕业院校": "school",
        "专业": "major",
        "学历": "degree",
        "学位": "degree",
        "最高学历": "highest_degree",
        "个人网站": "website",
        "网站": "website",
        "代码仓库": "github",
        "期望薪资": "expected_salary",
    }
    for raw_line in text.splitlines():
        line = raw_line.strip(" -\t")
        if not line:
            continue
        match = re.match(r"^([\u4e00-\u9fa5A-Za-z_/（）() ]{2,12})[:：]\s*(.+)$", line)
        if not match:
            continue
        key = aliases.get(match.group(1).strip())
        value = match.group(2).strip()
        if key and value:
            facts[key] = value
    return facts


def _normalize_resume_data(data: dict[str, Any], payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    data = data if isinstance(data, dict) else {}
    basics = data.setdefault("basics", {})
    if not isinstance(basics, dict):
        basics = {}
        data["basics"] = basics
    basics.setdefault("avatar", "")
    if not isinstance(basics.get("custom_fields"), list):
        basics["custom_fields"] = []
    field_config = basics.get("field_config")
    if not isinstance(field_config, dict):
        field_config = {}
        basics["field_config"] = field_config
    for key, cfg in DEFAULT_FIELD_CONFIG.items():
        current = field_config.get(key)
        if not isinstance(current, dict):
            current = {}
        field_config[key] = {**cfg, **current, "label": cfg["label"]}

    summary = data.setdefault("summary", {"content": ""})
    if isinstance(summary, str):
        data["summary"] = {"content": summary}
    elif not isinstance(summary, dict):
        data["summary"] = {"content": ""}
    else:
        summary.setdefault("content", "")

    for key in ["education", "skills", "work", "projects", "awards", "custom_sections"]:
        if not isinstance(data.get(key), list):
            data[key] = []

    payload = payload or {}
    facts = _extract_labeled_facts(str(payload.get("personal_info") or ""))
    for fact_key in ["name", "phone", "email", "status", "location", "highest_degree", "website", "github", "expected_salary"]:
        if facts.get(fact_key) and not basics.get(fact_key):
            basics[fact_key] = facts[fact_key]
    if facts.get("degree") and not basics.get("highest_degree"):
        basics["highest_degree"] = facts["degree"]

    if facts.get("school") or facts.get("major") or facts.get("degree"):
        if not data["education"]:
            data["education"].append({"id": "edu_1", "school": "", "major": "", "degree": "", "start_date": "", "end_date": "", "description": ""})
        first_education = data["education"][0]
        if isinstance(first_education, dict):
            if facts.get("school") and not first_education.get("school"):
                first_education["school"] = facts["school"]
            if facts.get("major") and not first_education.get("major"):
                first_education["major"] = facts["major"]
            if facts.get("degree") and not first_education.get("degree"):
                first_education["degree"] = facts["degree"]

    layout = data.setdefault("layout", {})
    layout["hidden_sections"] = [key for key in layout.get("hidden_sections", []) if key != "basics"] if isinstance(layout.get("hidden_sections"), list) else []
    section_order = layout.get("section_order")
    layout["section_order"] = section_order if isinstance(section_order, list) and section_order else BUILT_IN_SECTIONS.copy()
    for key in BUILT_IN_SECTIONS:
        if key not in layout["section_order"]:
            layout["section_order"].append(key)
    layout["section_order"] = ["basics"] + [key for key in layout["section_order"] if key != "basics"]
    section_titles = layout.setdefault("section_titles", {})
    for key, title in BUILT_IN_TITLES.items():
        if not section_titles.get(key) or section_titles.get(key) == key:
            section_titles[key] = title
    return data


def _normalize_ai_payload(data: dict[str, Any], schema: type[T]) -> dict[str, Any]:
    if schema is ResumeGenerateResult:
        resume_data = data.get("resume_data")
        if not isinstance(resume_data, dict):
            for key in ["optimized_resume_data", "data", "result", "resume"]:
                if isinstance(data.get(key), dict):
                    resume_data = data[key]
                    break
        if isinstance(resume_data, dict) and isinstance(resume_data.get("resume_data"), dict):
            resume_data = resume_data["resume_data"]
        if "resume_data" not in data and _looks_like_resume_data(data):
            resume_data = data
            data = {"resume_data": resume_data, "template_id": "tech", "template_config": {}, "explanation": ""}
        elif isinstance(resume_data, dict):
            data["resume_data"] = resume_data
        if "resume_data" in data:
            template_id = data.get("template_id")
            if template_id not in {"classic", "tech", "modern", "blue_timeline"}:
                data["template_id"] = "tech"
            if not isinstance(data.get("template_config"), dict):
                data["template_config"] = {}
            data["explanation"] = _stringify_summary(data.get("explanation", ""))
            data["resume_data"] = _normalize_resume_data(data["resume_data"], {})
        return data

    if schema is ResumeOptimizeResult:
        if "optimized_resume_data" not in data:
            if "resume_data" in data and isinstance(data["resume_data"], dict):
                data["optimized_resume_data"] = data["resume_data"]
            elif _looks_like_resume_data(data):
                data = {"optimized_resume_data": data, "summary": "", "changes": [], "suggestions": []}
        if isinstance(data.get("optimized_resume_data"), dict):
            optimized_resume_data = data["optimized_resume_data"]
            if isinstance(optimized_resume_data.get("resume_data"), dict):
                optimized_resume_data = optimized_resume_data["resume_data"]
            data["optimized_resume_data"] = _normalize_resume_data(optimized_resume_data, {})
        data["summary"] = _stringify_summary(data.get("summary", ""))
        data.setdefault("changes", [])
        data.setdefault("suggestions", [])
        return data

    if schema is ResumeScoreResult:
        if isinstance(data.get("result"), dict):
            nested = data["result"]
            data = {**nested, **{key: value for key, value in data.items() if key != "result"}}
        data["summary"] = _clean_score_text(_localize_field_names(_stringify_summary(data.get("summary", ""))))
        if isinstance(data.get("details"), dict):
            details = []
            for dimension, value in data["details"].items():
                details.append(_normalize_score_detail(value, str(dimension)))
            data["details"] = details
        elif isinstance(data.get("details"), list):
            data["details"] = [_normalize_score_detail(item, f"评分维度 {index + 1}") for index, item in enumerate(data["details"])]
        else:
            data["details"] = []
        data.setdefault("details", [])
        detail_average = int(round(sum(item["score"] for item in data["details"]) / len(data["details"]))) if data["details"] else 0
        score = _safe_int(data.get("score", 0), 0)
        if (data.get("score") is None or data.get("score") == "" or score == 0) and detail_average > 0:
            score = detail_average
        data["score"] = max(0, min(score, 100))
        if not data.get("level"):
            data["level"] = "优秀" if data["score"] >= 85 else "良好" if data["score"] >= 70 else "待优化" if data["score"] >= 55 else "需完善"
        data.setdefault("strengths", [])
        data.setdefault("weaknesses", [])
        data.setdefault("missing_keywords", [])
        data.setdefault("suggestions", [])
        for key in ["strengths", "weaknesses", "missing_keywords", "suggestions"]:
            data[key] = _clean_score_text(_localize_field_names(data.get(key, [])))
        return data

    if schema is JdOptimizeResult:
        if "optimized_resume_data" not in data:
            if isinstance(data.get("resume_data"), dict):
                data["optimized_resume_data"] = data["resume_data"]
            elif _looks_like_resume_data(data):
                data = {
                    "job_keywords": {},
                    "match_analysis": {},
                    "optimized_resume_data": data,
                    "score": 0,
                    "suggestions": [],
                }
        data["job_keywords"] = data.get("job_keywords") if isinstance(data.get("job_keywords"), dict) else {}
        data["match_analysis"] = data.get("match_analysis") if isinstance(data.get("match_analysis"), dict) else {}
        if isinstance(data.get("optimized_resume_data"), dict):
            optimized_resume_data = data["optimized_resume_data"]
            if isinstance(optimized_resume_data.get("resume_data"), dict):
                optimized_resume_data = optimized_resume_data["resume_data"]
            data["optimized_resume_data"] = _normalize_resume_data(optimized_resume_data, {})
        data["score"] = max(0, min(_safe_int(data.get("score", 0), 0), 100))
        data["suggestions"] = _clean_score_text(_localize_field_names(_string_list(data.get("suggestions", []))))
        return data

    if schema is ResumeChatResult:
        if isinstance(data.get("result"), dict):
            nested = data["result"]
            data = {**nested, **{key: value for key, value in data.items() if key != "result"}}
        data["reply"] = _clean_score_text(_localize_field_names(_stringify_summary(data.get("reply") or data.get("message") or data.get("content") or "")))
        data["suggestions"] = _clean_score_text(_localize_field_names(_string_list(data.get("suggestions", []))))
        optimized_resume_data = data.get("optimized_resume_data")
        if optimized_resume_data is None and isinstance(data.get("resume_data"), dict):
            optimized_resume_data = data["resume_data"]
        if isinstance(optimized_resume_data, dict):
            if isinstance(optimized_resume_data.get("resume_data"), dict):
                optimized_resume_data = optimized_resume_data["resume_data"]
            data["optimized_resume_data"] = _normalize_resume_data(optimized_resume_data, {})
        else:
            data["optimized_resume_data"] = None
        return data

    if schema is SectionOptimizeResult:
        if "optimized_section" not in data and "section_content" in data:
            data = {
                "optimized_section": data.get("section_content"),
                "changes": data.get("changes", []),
                "suggestions": data.get("suggestions", []),
            }
        if "optimized_section" not in data:
            data = {"optimized_section": data, "changes": [], "suggestions": []}
        if isinstance(data.get("optimized_section"), dict) and "section_content" in data["optimized_section"]:
            data["optimized_section"] = data["optimized_section"]["section_content"]
        data.setdefault("changes", [])
        data.setdefault("suggestions", [])
        data["changes"] = _clean_score_text(_localize_field_names(data.get("changes", [])))
        data["suggestions"] = _clean_score_text(_localize_field_names(data.get("suggestions", [])))
        return data

    return data


def _validate_json_content(content: Any, schema: type[T], payload: Optional[dict[str, Any]] = None) -> T:
    try:
        parsed = _parse_json_content(content)
    except AppException:
        parsed = _repair_json_content(content, f"修复 {schema.__name__} 的 JSON 输出")
    data = _normalize_ai_payload(parsed, schema)
    try:
        return schema.model_validate(data)
    except ValidationError as exc:
        repair_input = {"validation_error": str(exc), "raw_json": data}
        try:
            repaired = _repair_json_content(json.dumps(repair_input, ensure_ascii=False), f"根据校验错误修复 {schema.__name__} 的 JSON 结构")
            normalized = _normalize_ai_payload(repaired, schema)
            return schema.model_validate(normalized)
        except Exception:
            raise AppException(f"AI 输出结构校验失败：{exc}") from exc


def _invoke_json(prompt, payload: dict[str, Any], schema: type[T]) -> T:
    chain = prompt | get_llm()
    message = chain.invoke({"input_json": json.dumps(payload, ensure_ascii=False)})
    content = getattr(message, "content", message)
    return _validate_json_content(content, schema, payload)


def _chunk_text(chunk: Any) -> str:
    content = getattr(chunk, "content", chunk)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            elif item is not None:
                parts.append(str(item))
        return "".join(parts)
    return "" if content is None else str(content)


def stream_json_events(prompt, payload: dict[str, Any], schema: type[T]):
    yield {"type": "start"}
    chunks: list[str] = []
    try:
        chain = prompt | get_llm()
        for chunk in chain.stream({"input_json": json.dumps(payload, ensure_ascii=False)}):
            text = _chunk_text(chunk)
            if not text:
                continue
            chunks.append(text)
            yield {"type": "delta", "text": text}
        result = _validate_json_content("".join(chunks), schema, payload)
        if schema is ResumeGenerateResult:
            result.resume_data = _normalize_resume_data(result.resume_data, payload)  # type: ignore[attr-defined]
        yield {"type": "result", "data": result.model_dump()}
    except AppException as exc:
        yield {"type": "error", "message": exc.message}
    except Exception as exc:
        raw_message = str(exc) or "AI 生成失败"
        message = "AI 服务连接失败，请检查模型配置或网络连通性" if "connection" in raw_message.lower() else raw_message
        yield {"type": "error", "message": message}


def generate_resume_chain(payload: dict[str, Any]) -> ResumeGenerateResult:
    result = _invoke_json(GENERATE_RESUME_PROMPT, payload, ResumeGenerateResult)
    result.resume_data = _normalize_resume_data(result.resume_data, payload)
    return result


def score_resume_chain(payload: dict[str, Any]) -> ResumeScoreResult:
    return _invoke_json(SCORE_RESUME_PROMPT, payload, ResumeScoreResult)


def optimize_section_chain(payload: dict[str, Any]) -> SectionOptimizeResult:
    return _invoke_json(OPTIMIZE_SECTION_PROMPT, payload, SectionOptimizeResult)


def optimize_resume_chain(payload: dict[str, Any]) -> ResumeOptimizeResult:
    return _invoke_json(OPTIMIZE_RESUME_PROMPT, payload, ResumeOptimizeResult)


def optimize_by_jd_chain(payload: dict[str, Any]) -> JdOptimizeResult:
    return _invoke_json(JD_OPTIMIZE_PROMPT, payload, JdOptimizeResult)


def resume_chat_chain(payload: dict[str, Any]) -> ResumeChatResult:
    return _invoke_json(CHAT_RESUME_PROMPT, payload, ResumeChatResult)


def resume_chat_reply_stream(payload: dict[str, Any]):
    chain = CHAT_RESUME_REPLY_PROMPT | get_llm()
    for chunk in chain.stream({"input_json": json.dumps(payload, ensure_ascii=False)}):
        text = _chunk_text(chunk)
        if text:
            yield text


def resume_chat_action_reply_stream(payload: dict[str, Any]):
    chain = CHAT_ACTION_REPLY_PROMPT | get_llm()
    for chunk in chain.stream({"input_json": json.dumps(payload, ensure_ascii=False)}):
        text = _chunk_text(chunk)
        if text:
            yield text


def generate_resume_stream(payload: dict[str, Any]):
    return stream_json_events(GENERATE_RESUME_PROMPT, payload, ResumeGenerateResult)


def score_resume_stream(payload: dict[str, Any]):
    return stream_json_events(SCORE_RESUME_PROMPT, payload, ResumeScoreResult)


def optimize_section_stream(payload: dict[str, Any]):
    return stream_json_events(OPTIMIZE_SECTION_PROMPT, payload, SectionOptimizeResult)


def optimize_by_jd_stream(payload: dict[str, Any]):
    return stream_json_events(JD_OPTIMIZE_PROMPT, payload, JdOptimizeResult)


def generate_summary_chain(payload: dict[str, Any]) -> SummaryGenerateResult:
    return _invoke_json(SUMMARY_PROMPT, payload, SummaryGenerateResult)


def optimize_project_chain(payload: dict[str, Any]) -> ProjectOptimizeResult:
    return _invoke_json(PROJECT_PROMPT, payload, ProjectOptimizeResult)
