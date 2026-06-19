from __future__ import annotations

from typing import Any, Optional

from app.schemas.resume import default_resume_data, default_template_config
from app.services.preview_service import render_resume_html


TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "classic",
        "name": "经典单栏",
        "category": "通用",
        "preview_image": "",
        "is_pro": False,
        "config_schema": {"theme_color": "#111827"},
    },
    {
        "template_id": "tech",
        "name": "技术岗位",
        "category": "技术",
        "preview_image": "",
        "is_pro": False,
        "config_schema": {"theme_color": "#2563eb"},
    },
    {
        "template_id": "modern",
        "name": "现代双栏",
        "category": "互联网",
        "preview_image": "",
        "is_pro": False,
        "config_schema": {"theme_color": "#0f766e"},
    },
    {
        "template_id": "blue_timeline",
        "name": "蓝色时间轴",
        "category": "技术",
        "preview_image": "",
        "is_pro": False,
        "config_schema": {"theme_color": "#4673f4"},
    },
]


def _preview_avatar() -> str:
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 210'%3E"
        "%3Crect width='160' height='210' fill='%23f8fafc'/%3E"
        "%3Cpath d='M20 210 C20 145 40 130 80 130 C120 130 140 145 140 210 Z' fill='%231e3a8a'/%3E"
        "%3Cpath d='M55 133 L80 175 L105 133 C90 140 70 140 55 133 Z' fill='%23ffffff'/%3E"
        "%3Crect x='68' y='105' width='24' height='40' fill='%23e5c3ad'/%3E"
        "%3Ccircle cx='80' cy='72' r='36' fill='%23111827'/%3E"
        "%3Ccircle cx='80' cy='86' r='32' fill='%23f7d9c4'/%3E"
        "%3C/svg%3E"
    )


def _preview_resume_data() -> dict[str, Any]:
    data = default_resume_data()
    data["basics"].update(
        {
            "name": "Elliot",
            "title": "Java后端开发工程师",
            "phone": "18800000000",
            "email": "admin@cgz233.cn",
            "status": "在读",
            "location": "杭州",
            "highest_degree": "本科",
            "website": "https://www.cgz233.cn",
            "avatar": _preview_avatar(),
            "custom_fields": [
                {"id": "age", "label": "年龄", "value": "男22岁", "icon": "Info", "row": 1, "order": 3},
                {"id": "target", "label": "岗位", "value": "Java后端开发工程师", "icon": "IdCard", "row": 2, "order": 2},
            ],
        }
    )
    data["basics"]["field_config"]["status"] = {"label": "当前状态", "icon": "Tag", "row": 2, "order": 1}
    data["basics"]["field_config"]["location"] = {"label": "地点", "icon": "MapPin", "row": 2, "order": 3}
    data["basics"]["field_config"]["highest_degree"] = {"label": "最高学历", "icon": "CalendarCheck", "row": 3, "order": 1}
    data["basics"]["field_config"]["website"] = {"label": "个人网站", "icon": "Globe", "row": 3, "order": 2}
    data["summary"]["content"] = "熟悉 Java、Spring Boot、Spring Cloud、MySQL、Redis 与 LangChain，具备从需求分析、接口设计到上线部署的完整项目经验。"
    data["skills"] = [
        {
            "id": "skill_1",
            "name": "专业技能",
            "keywords": [],
            "description": "- 熟练掌握 Java 核心基础知识，熟悉常见设计模式，具备良好的编码习惯。\n- 熟练使用 Spring、Spring MVC、Spring Boot，掌握 AOP 编程思想。\n- 熟悉 MySQL、Redis 等数据库与缓存的日常操作，熟悉 MyBatis-Plus 框架。\n- 掌握 Vue、uni-app 等前端开发框架，了解大模型应用开发流程。",
        }
    ]
    data["work"] = [
        {
            "id": "work_1",
            "company": "零度极客有限公司",
            "position": "Java开发",
            "start_date": "2024.09",
            "end_date": "2025.03",
            "description": "软件开发部  济南",
            "highlights": [
                "负责前后端开发工作，后端基于 Spring Boot 构建接口，前端使用 uni-app 实现移动端应用。",
                "参与需求分析、系统设计、接口联调与接口测试。",
                "使用 Redis 实现缓存机制，提升系统响应速度。",
            ],
        }
    ]
    data["projects"] = [
        {
            "id": "project_1",
            "name": "智能任务管理平台",
            "role": "",
            "start_date": "",
            "end_date": "",
            "tech_stack": "SpringBoot、MySQL、Redis、MyBatis-Plus、JWT、uniapp、Vue",
            "description": "项目描述：该项目是一个基于 SpringBoot 与 uniapp 构建的线下收款小程序系统，主要面向线下商家收款场景。",
            "highlights": [
                "基于 JWT 实现用户登录与身份校验，结合拦截器存储用户上下文信息。",
                "引入 Redis 缓存高频访问数据，并使用 Spring Cache 简化缓存逻辑。",
            ],
        }
    ]
    data["awards"] = []
    data["layout"]["section_order"] = ["basics", "skills", "work", "projects"]
    data["layout"]["section_titles"]["skills"] = "专业技能"
    data["layout"]["section_titles"]["work"] = "工作经历"
    data["layout"]["section_titles"]["projects"] = "项目经历"
    return data


def _with_preview(template: dict[str, Any]) -> dict[str, Any]:
    item = template.copy()
    config = default_template_config(item["template_id"])
    config.update(item.get("config_schema") or {})
    config["template_id"] = item["template_id"]
    item["preview_html"] = render_resume_html(_preview_resume_data(), item["template_id"], config)
    return item


def list_templates() -> list[dict[str, Any]]:
    return [_with_preview(item) for item in TEMPLATES]


def get_template(template_id: str) -> Optional[dict[str, Any]]:
    template = next((item for item in TEMPLATES if item["template_id"] == template_id), None)
    return _with_preview(template) if template else None
