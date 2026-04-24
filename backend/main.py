"""FastAPI 主应用"""
import asyncio
import json
import uuid
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent import chat, chat_stream, clear_session, get_session_messages
from config import get_settings
from rag_engine import delete_document, get_document_preview, ingest_document, list_documents, resolve_document_file

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


@app.get("/documents/{doc_id}/preview")
async def preview_document(doc_id: str):
    """获取文档预览内容"""
    preview = get_document_preview(doc_id)
    if not preview:
        raise HTTPException(status_code=404, detail="文档不存在或无法预览")
    return preview


@app.get("/documents/{doc_id}/file")
async def get_document_file(doc_id: str):
    """获取文档原始文件，便于 PDF 等格式直接预览"""
    resolved = resolve_document_file(doc_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="文档不存在")

    file_path = resolved["file_path"]
    filename = resolved["filename"]
    suffix = resolved["suffix"]
    media_type = "application/pdf" if suffix == ".pdf" else None

    return FileResponse(
        path=file_path,
        media_type=media_type,
        content_disposition_type="inline",
    )


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
