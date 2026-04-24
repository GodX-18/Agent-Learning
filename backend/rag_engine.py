"""RAG 引擎：文档处理、向量存储、检索"""
import uuid
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from docx import Document as DocxDocument

from config import get_settings

settings = get_settings()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        # 阿里云 DashScope 只接受纯字符串，不支持 token 数组格式
        check_embedding_ctx_length=False,
    )


def get_vector_store(collection_name: str = "documents") -> Chroma:
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def load_document(file_path: str) -> List[Document]:
    """根据文件类型加载文档"""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".docx", ".doc"):
        loader = Docx2txtLoader(file_path)
    elif ext in (".txt", ".md"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件类型: {ext}")
    return loader.load()


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    )
    return splitter.split_documents(docs)


async def ingest_document(
    file_content: bytes,
    filename: str,
    collection_name: str = "documents",
) -> dict:
    """处理并索引上传的文档"""
    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}_{filename}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    docs = load_document(str(file_path))
    chunks = split_documents(docs)

    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["filename"] = filename

    vs = get_vector_store(collection_name)
    ids = vs.add_documents(chunks)

    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunks": len(chunks),
        "chunk_ids": ids,
    }


def retrieve_documents(
    query: str,
    collection_name: str = "documents",
    k: int = 4,
    filter_doc_id: Optional[str] = None,
) -> List[Document]:
    """从向量库检索相关文档"""
    vs = get_vector_store(collection_name)
    search_kwargs = {"k": k}
    if filter_doc_id:
        search_kwargs["filter"] = {"doc_id": filter_doc_id}

    retriever = vs.as_retriever(
        search_type="similarity", search_kwargs=search_kwargs)
    return retriever.invoke(query)


def list_documents(collection_name: str = "documents") -> List[dict]:
    """列出已索引的文档"""
    vs = get_vector_store(collection_name)
    collection = vs._collection
    results = collection.get(include=["metadatas"])

    seen = {}
    for meta in results.get("metadatas", []):
        if meta and "doc_id" in meta:
            doc_id = meta["doc_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta.get("filename", "未知"),
                }
    return list(seen.values())


def delete_document(doc_id: str, collection_name: str = "documents") -> bool:
    """删除指定文档的所有向量"""
    vs = get_vector_store(collection_name)
    collection = vs._collection
    results = collection.get(where={"doc_id": doc_id})
    ids_to_delete = results.get("ids", [])
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        return True
    return False


def resolve_document_file(doc_id: str, collection_name: str = "documents") -> Optional[dict]:
    """解析文档元数据与原始文件路径"""
    vs = get_vector_store(collection_name)
    collection = vs._collection
    results = collection.get(where={"doc_id": doc_id}, include=["metadatas"])

    metadatas = results.get("metadatas", [])
    if not metadatas:
        return None

    metadata = next((meta for meta in metadatas if meta), None)
    if not metadata:
        return None

    filename = metadata.get("filename")
    if not filename:
        return None

    matches = list(UPLOAD_DIR.glob(f"{doc_id}_*"))
    if not matches:
        return None

    file_path = matches[0]
    return {
        "doc_id": doc_id,
        "filename": filename,
        "file_path": file_path,
        "suffix": file_path.suffix.lower(),
    }


def get_document_preview(doc_id: str, collection_name: str = "documents") -> Optional[dict]:
    """读取指定文档的原始内容，供前端预览使用"""
    resolved = resolve_document_file(doc_id, collection_name)
    if not resolved:
        return None

    filename = resolved["filename"]
    file_path = resolved["file_path"]
    suffix = resolved["suffix"]

    if suffix == ".pdf":
        return {
            "doc_id": doc_id,
            "filename": filename,
            "file_type": "pdf",
            "content": "",
        }

    if suffix in (".txt", ".md"):
        content = file_path.read_text(encoding="utf-8")
    elif suffix in (".doc", ".docx"):
        doc = DocxDocument(BytesIO(file_path.read_bytes()))
        content = "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    else:
        raise ValueError(f"不支持预览的文件类型: {suffix}")

    return {
        "doc_id": doc_id,
        "filename": filename,
        "file_type": suffix.lstrip("."),
        "content": content,
    }
