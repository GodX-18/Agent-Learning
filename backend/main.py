"""FastAPI 主应用"""
import asyncio
import json
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent import chat, chat_stream, clear_session, get_session_messages
from config import get_settings
from course_agent import (
    CourseOutline,
    CourseTemplate,
    build_course_file_tree,
    generate_chapter_markdown,
    generate_course_outline,
    get_course_dir,
    list_course_templates,
    load_outline,
    read_markdown_files,
    save_course_to_disk,
)
from rag_engine import delete_document, ingest_document, list_documents

settings = get_settings()

app = FastAPI(
    title="LangChain RAG 智能体 API",
    description="基于 LangChain 的 RAG 智能体，支持文档上传、问答和工具调用",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 数据模型 ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True


class ChatResponse(BaseModel):
    answer: str
    session_id: str


class SessionInfo(BaseModel):
    session_id: str
    messages: list


class CourseOutlineRequest(BaseModel):
    topic: str
    template: CourseTemplate = CourseTemplate.STANDARD
    use_rag: bool = False
    kb_ids: List[str] = []
    custom_instruction: str = ""


class CourseGenerateRequest(BaseModel):
    topic: str
    template: CourseTemplate = CourseTemplate.STANDARD
    use_rag: bool = False
    kb_ids: List[str] = []
    custom_instruction: str = ""
    outline: Optional[Dict[str, Any]] = None


class CourseOutlineUpdateRequest(BaseModel):
    task_id: Optional[str] = None
    outline: Dict[str, Any]


class CourseTaskResponse(BaseModel):
    task_id: str
    status: str


# 任务状态（内存）
COURSE_TASKS: Dict[str, Dict[str, Any]] = {}


def _emit_course_event(task_id: str, event_type: str, data: Dict[str, Any]) -> None:
    task = COURSE_TASKS.get(task_id)
    if not task:
        return
    task["events"].append({"event": event_type, "data": data})
    task["updated"].set()


async def _run_course_generation(task_id: str, request: CourseGenerateRequest) -> None:
    task = COURSE_TASKS[task_id]
    task["status"] = "running"
    _emit_course_event(task_id, "progress", {"stage": "start", "message": "任务已启动"})

    try:
        if request.outline:
            outline = CourseOutline.model_validate(request.outline)
            _emit_course_event(task_id, "progress", {"stage": "outline", "message": "使用用户编辑后的大纲"})
        else:
            _emit_course_event(task_id, "progress", {"stage": "outline", "message": "正在生成课程大纲"})
            outline = await generate_course_outline(
                topic=request.topic,
                template=request.template,
                use_rag=request.use_rag,
                kb_doc_ids=request.kb_ids,
                custom_instruction=request.custom_instruction,
            )

        chapter_contents: Dict[str, str] = {}
        total = max(len(outline.chapters), 1)
        for idx, chapter in enumerate(outline.chapters, start=1):
            _emit_course_event(
                task_id,
                "progress",
                {
                    "stage": "generating",
                    "current": idx,
                    "total": total,
                    "chapter": chapter.title,
                },
            )
            chapter_contents[chapter.id] = await generate_chapter_markdown(
                topic=request.topic,
                template=request.template,
                chapter=chapter,
                use_rag=request.use_rag,
                kb_doc_ids=request.kb_ids,
            )

        course_dir = save_course_to_disk(
            task_id=task_id,
            topic=request.topic,
            template=request.template,
            outline=outline,
            chapter_contents=chapter_contents,
        )
        task["status"] = "completed"
        task["course_dir"] = str(course_dir)
        _emit_course_event(task_id, "done", {"task_id": task_id, "status": "completed"})
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        _emit_course_event(task_id, "error", {"task_id": task_id, "status": "failed", "error": str(e)})


# ─── 健康检查 ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model": settings.openai_model,
        "embedding_model": settings.embedding_model,
    }


# ─── 文档管理接口 ──────────────────────────────────────────────────────────────

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    allowed_types = {".pdf", ".txt", ".md", ".docx", ".doc"}
    suffix = "." + \
        file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if suffix not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {suffix}，支持: {', '.join(allowed_types)}",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 {settings.max_upload_size_mb}MB",
        )

    result = await ingest_document(content, file.filename)
    return {
        "success": True,
        "message": f"文档 '{file.filename}' 已成功上传并索引",
        **result,
    }


@app.get("/documents")
async def get_documents():
    """获取已索引的文档列表"""
    docs = list_documents()
    return {"documents": docs, "total": len(docs)}


@app.delete("/documents/{doc_id}")
async def remove_document(doc_id: str):
    """从知识库中删除文档"""
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"success": True, "message": "文档已删除"}


# ─── 对话接口 ──────────────────────────────────────────────────────────────────

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """发送消息（流式或非流式）"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    session_id = request.session_id or str(uuid.uuid4())

    if request.stream:
        async def event_generator():
            try:
                async for chunk in chat_stream(request.message, session_id):
                    data = json.dumps(
                        {"chunk": chunk, "session_id": session_id}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
            except Exception as e:
                error_data = json.dumps(
                    {"error": str(e), "session_id": session_id}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        answer = await chat(request.message, session_id)
        return ChatResponse(answer=answer, session_id=session_id)


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话历史"""
    messages = get_session_messages(session_id)
    return SessionInfo(session_id=session_id, messages=messages)


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """清除会话历史"""
    clear_session(session_id)
    return {"success": True, "message": "会话已清除"}


# ─── 课程生成接口 ──────────────────────────────────────────────────────────────

@app.get("/course/templates")
async def get_course_templates():
    return {"templates": list_course_templates()}


@app.post("/course/outline")
async def create_course_outline(request: CourseOutlineRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="课程主题不能为空")

    try:
        outline = await generate_course_outline(
            topic=request.topic,
            template=request.template,
            use_rag=request.use_rag,
            kb_doc_ids=request.kb_ids,
            custom_instruction=request.custom_instruction,
        )
    except Exception as e:
        err_str = str(e)
        if "529" in err_str or "overloaded" in err_str.lower():
            raise HTTPException(
                status_code=503,
                detail="模型服务当前繁忙，请稍后重试。" + err_str[:200],
            )
        raise HTTPException(status_code=500, detail=f"大纲生成失败：{err_str[:300]}")

    return {"outline": outline.model_dump(), "template": request.template.value}


@app.put("/course/outline")
async def update_course_outline(request: CourseOutlineUpdateRequest):
    outline = CourseOutline.model_validate(request.outline)
    if request.task_id and request.task_id in COURSE_TASKS:
        COURSE_TASKS[request.task_id]["outline"] = outline.model_dump()
    return {"success": True, "outline": outline.model_dump()}


@app.post("/course/generate", response_model=CourseTaskResponse)
async def generate_course(request: CourseGenerateRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="课程主题不能为空")

    task_id = f"course_{uuid.uuid4().hex[:12]}"
    COURSE_TASKS[task_id] = {
        "status": "queued",
        "events": [],
        "updated": asyncio.Event(),
        "error": None,
        "course_dir": None,
        "outline": request.outline,
    }
    asyncio.create_task(_run_course_generation(task_id, request))
    return CourseTaskResponse(task_id=task_id, status="queued")


@app.get("/course/status/{task_id}")
async def course_status(task_id: str):
    if task_id not in COURSE_TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_generator():
        index = 0
        while True:
            task = COURSE_TASKS.get(task_id)
            if not task:
                break

            events = task["events"]
            while index < len(events):
                event = events[index]
                index += 1
                yield f"event: {event['event']}\n"
                yield f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

            if task["status"] in {"completed", "failed"} and index >= len(events):
                break

            task["updated"].clear()
            try:
                await asyncio.wait_for(task["updated"].wait(), timeout=20)
            except asyncio.TimeoutError:
                yield "event: heartbeat\n"
                yield "data: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/course/result/{task_id}")
async def course_result(task_id: str):
    task = COURSE_TASKS.get(task_id)
    if task and task["status"] != "completed":
        return {
            "task_id": task_id,
            "status": task["status"],
            "error": task.get("error"),
        }

    if task:
        course_dir = (
            Path(task["course_dir"])
            if task["course_dir"]
            else get_course_dir(task_id)
        )
        task_status = task["status"]
    else:
        # 服务重启后内存任务会丢失，允许直接从磁盘恢复历史课程
        course_dir = get_course_dir(task_id)
        task_status = "completed"

    if not course_dir.exists():
        raise HTTPException(status_code=404, detail="课程结果不存在")

    try:
        meta, outline = load_outline(course_dir)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="课程结果文件不完整") from exc

    return {
        "task_id": task_id,
        "status": task_status,
        "meta": meta,
        "outline": outline.model_dump(),
        "tree": build_course_file_tree(course_dir),
        "markdown_files": read_markdown_files(course_dir),
    }


@app.get("/course/download/{task_id}")
async def download_course(task_id: str):
    task = COURSE_TASKS.get(task_id)
    if task and task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    if task:
        course_dir = (
            Path(task["course_dir"])
            if task["course_dir"]
            else get_course_dir(task_id)
        )
    else:
        # 支持下载历史课程（无内存任务状态）
        course_dir = get_course_dir(task_id)

    if not course_dir.exists():
        raise HTTPException(status_code=404, detail="课程目录不存在")

    zip_path = course_dir.parent / f"{task_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in course_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(course_dir))

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{task_id}.zip",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
