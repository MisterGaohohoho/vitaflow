from __future__ import annotations

from typing import Optional, Union

import bleach
import markdown


ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "code",
    "pre",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "a",
    "span",
]
ALLOWED_ATTRIBUTES = {"a": ["href", "title", "target", "rel"], "span": ["class"]}


def markdown_to_safe_html(text: Optional[Union[str, list[str]]]) -> str:
    if text is None:
        return ""
    if isinstance(text, list):
        text = "\n".join(f"- {item}" for item in text if item)
    raw_html = markdown.markdown(str(text), extensions=["extra", "sane_lists"])
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
