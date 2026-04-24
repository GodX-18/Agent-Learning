"""课程生成智能体：大纲生成、章节生成、文件树存储。"""
from __future__ import annotations

import json
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import get_settings
from rag_engine import retrieve_documents

settings = get_settings()

COURSE_STORAGE_DIR = Path("./course_storage")
COURSE_STORAGE_DIR.mkdir(exist_ok=True)


class CourseTemplate(str, Enum):
    STANDARD = "standard"
    COMPACT = "compact"
    DETAILED = "detailed"


class CourseSection(BaseModel):
    id: str
    title: str
    goals: List[str] = Field(default_factory=list)


class CourseChapter(BaseModel):
    id: str
    title: str
    summary: str = ""
    sections: List[CourseSection] = Field(default_factory=list)


class CourseOutline(BaseModel):
    title: str
    audience: str = ""
    prerequisites: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    chapters: List[CourseChapter] = Field(default_factory=list)


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.65,
        streaming=False,
        extra_body={"reasoning_split": True},
    )


def list_course_templates() -> List[Dict[str, str]]:
    return [
        {
            "id": CourseTemplate.STANDARD.value,
            "name": "标准课程",
            "description": "章-节-知识点-练习-小结，适合主流在线课程。",
        },
        {
            "id": CourseTemplate.COMPACT.value,
            "name": "精简课程",
            "description": "更短章节与要点列表，适合快速入门。",
        },
        {
            "id": CourseTemplate.DETAILED.value,
            "name": "详细课程",
            "description": "更深的知识点、案例和综合练习。",
        },
    ]


def _template_requirement(template: CourseTemplate) -> str:
    if template == CourseTemplate.COMPACT:
        return (
            "每章保持 2~3 节，每节 2~3 个目标，内容紧凑，强调可快速学习。"
        )
    if template == CourseTemplate.DETAILED:
        return (
            "每章保持 3~5 节，每节包含理论、案例和实践目标，适合系统化深度学习。"
        )
    return "每章保持 3~4 节，每节 2~4 个学习目标，兼顾理论与实操。"


def _extract_json(text: str) -> Dict[str, Any]:
    # 优先处理 ```json ... ``` 代码块（非贪婪匹配内部大括号对）
    code_block = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # 使用 raw_decode 从第一个 `{` 处解析，忽略后续多余文本
    decoder = json.JSONDecoder()
    start = text.find("{")
    if start != -1:
        try:
            obj, _ = decoder.raw_decode(text, start)
            return obj  # type: ignore[return-value]
        except json.JSONDecodeError:
            pass

    return json.loads(text)


def _retrieve_rag_context(topic: str, kb_doc_ids: Optional[List[str]]) -> str:
    snippets: List[str] = []
    if kb_doc_ids:
        for doc_id in kb_doc_ids:
            for doc in retrieve_documents(topic, k=2, filter_doc_id=doc_id):
                source = doc.metadata.get("filename", "未知")
                snippets.append(f"[{source}] {doc.page_content[:600]}")
    else:
        for doc in retrieve_documents(topic, k=4):
            source = doc.metadata.get("filename", "未知")
            snippets.append(f"[{source}] {doc.page_content[:600]}")
    return "\n\n".join(snippets[:8])


async def generate_course_outline(
    topic: str,
    template: CourseTemplate,
    use_rag: bool = False,
    kb_doc_ids: Optional[List[str]] = None,
    custom_instruction: str = "",
) -> CourseOutline:
    llm = _build_llm()
    rag_context = _retrieve_rag_context(topic, kb_doc_ids) if use_rag else ""

    prompt = f"""
你是课程设计专家，请为主题生成课程大纲。

主题：{topic}
模板：{template.value}
模板要求：{_template_requirement(template)}
额外要求：{custom_instruction or "无"}

请只输出 JSON，结构必须是：
{{
  "title": "课程标题",
  "audience": "目标人群",
  "prerequisites": ["前置知识1"],
  "learning_outcomes": ["学习成果1"],
  "chapters": [
    {{
      "id": "ch1",
      "title": "第一章标题",
      "summary": "章节简介",
      "sections": [
        {{
          "id": "ch1-s1",
          "title": "小节标题",
          "goals": ["掌握目标1", "掌握目标2"]
        }}
      ]
    }}
  ]
}}
"""
    if rag_context:
        prompt += f"\n参考资料片段（请谨慎引用，不可臆造）：\n{rag_context}\n"

    result = await llm.ainvoke(prompt)
    parsed = _extract_json(result.content if isinstance(result.content, str) else str(result.content))
    return CourseOutline.model_validate(parsed)


async def generate_chapter_markdown(
    topic: str,
    template: CourseTemplate,
    chapter: CourseChapter,
    use_rag: bool = False,
    kb_doc_ids: Optional[List[str]] = None,
) -> str:
    llm = _build_llm()
    rag_context = _retrieve_rag_context(f"{topic} {chapter.title}", kb_doc_ids) if use_rag else ""

    section_lines = "\n".join(
        f"- {section.title}: {', '.join(section.goals) if section.goals else '核心知识点'}"
        for section in chapter.sections
    )

    prompt = f"""
你是课程内容作者，请为章节生成 Markdown 内容。

课程主题：{topic}
章节标题：{chapter.title}
章节简介：{chapter.summary}
模板：{template.value}
小节与目标：
{section_lines or "- 无"}

输出要求：
1. 仅输出 Markdown 正文，不要解释。
2. 至少包含：章节导学、小节内容、示例或案例、练习题、本章总结。
3. 语言简洁、教学友好、中文。
"""
    if rag_context:
        prompt += (
            "\n可参考资料（可引用但不可捏造）：\n"
            f"{rag_context}\n"
        )

    result = await llm.ainvoke(prompt)
    content = result.content if isinstance(result.content, str) else str(result.content)
    return content.strip()


def _slugify(name: str) -> str:
    sanitized = re.sub(r"[^\w\-\u4e00-\u9fa5]+", "-", name).strip("-")
    return sanitized or "chapter"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_course_to_disk(
    task_id: str,
    topic: str,
    template: CourseTemplate,
    outline: CourseOutline,
    chapter_contents: Dict[str, str],
) -> Path:
    base_dir = COURSE_STORAGE_DIR / task_id
    base_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "task_id": task_id,
        "topic": topic,
        "template": template.value,
        "created_at": datetime.utcnow().isoformat(),
        "title": outline.title,
        "chapters": len(outline.chapters),
    }
    _write_text(base_dir / "course_meta.json", json.dumps(meta, ensure_ascii=False, indent=2))
    _write_text(base_dir / "outline.json", outline.model_dump_json(indent=2))

    outcomes = [f"- {item}" for item in outline.learning_outcomes] or ["- 待完善"]
    root_readme = [
        f"# {outline.title}",
        "",
        f"- 主题：{topic}",
        f"- 模板：{template.value}",
        f"- 目标人群：{outline.audience or '未指定'}",
        "",
        "## 学习成果",
        *outcomes,
        "",
        "## 章节目录",
    ]
    for idx, chapter in enumerate(outline.chapters, start=1):
        root_readme.append(f"- 第{idx}章：{chapter.title}")
    _write_text(base_dir / "README.md", "\n".join(root_readme).strip() + "\n")

    for idx, chapter in enumerate(outline.chapters, start=1):
        chapter_dir = base_dir / f"chapter_{idx:02d}_{_slugify(chapter.title)}"
        chapter_dir.mkdir(parents=True, exist_ok=True)

        chapter_overview = [
            f"# 第{idx}章：{chapter.title}",
            "",
            chapter.summary or "本章将帮助你掌握关键知识。",
            "",
            "## 小节",
        ]
        for section in chapter.sections:
            chapter_overview.append(f"- {section.title}")
        _write_text(chapter_dir / "README.md", "\n".join(chapter_overview).strip() + "\n")

        chapter_content = chapter_contents.get(chapter.id, "")
        _write_text(chapter_dir / "content.md", chapter_content + "\n")

    return base_dir


def build_course_file_tree(course_dir: Path) -> List[Dict[str, Any]]:
    def _build(path: Path) -> Dict[str, Any]:
        if path.is_file():
            return {
                "name": path.name,
                "type": "file",
                "path": str(path.relative_to(course_dir)),
            }
        children = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
        return {
            "name": path.name,
            "type": "directory",
            "path": str(path.relative_to(course_dir)) if path != course_dir else ".",
            "children": [_build(item) for item in children],
        }

    return [_build(course_dir)]


def read_markdown_files(course_dir: Path) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for file_path in course_dir.rglob("*.md"):
        rel_path = str(file_path.relative_to(course_dir))
        results[rel_path] = file_path.read_text(encoding="utf-8")
    return results


def get_course_dir(task_id: str) -> Path:
    return COURSE_STORAGE_DIR / task_id


def load_outline(path: Path) -> Tuple[Dict[str, Any], CourseOutline]:
    meta = json.loads((path / "course_meta.json").read_text(encoding="utf-8"))
    outline = CourseOutline.model_validate_json((path / "outline.json").read_text(encoding="utf-8"))
    return meta, outline
