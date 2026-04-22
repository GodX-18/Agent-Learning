"""LangChain 1.x Agent：集成 RAG 工具 + 对话记忆（MemorySaver）"""
from typing import AsyncIterator, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from config import get_settings
from rag_engine import retrieve_documents

settings = get_settings()

# 全局共享 checkpointer（线程安全的内存存储）
_memory = MemorySaver()


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.7,
        streaming=True,
    )


# ── 工具定义 ──────────────────────────────────────────────────────────────────

@tool
def search_documents(query: str) -> str:
    """在知识库中搜索与问题相关的文档内容。当需要回答关于已上传文档的问题时使用此工具。"""
    docs = retrieve_documents(query, k=4)
    if not docs:
        return "知识库中没有找到相关内容。"

    results = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("filename", "未知来源")
        page = doc.metadata.get("page", "")
        page_info = f" 第{int(page) + 1}页" if page != "" else ""
        results.append(f"[片段{i}] 来源：{source}{page_info}\n{doc.page_content}")

    return "\n\n---\n\n".join(results)


@tool
def get_current_time() -> str:
    """获取当前日期和时间。"""
    from datetime import datetime
    return datetime.now().strftime("当前时间：%Y年%m月%d日 %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。支持基本四则运算、幂运算等。示例：'2 + 3 * 4'"""
    try:
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


_TOOLS = [search_documents, get_current_time, calculate]

_SYSTEM_PROMPT = """你是一个智能助手，具备以下能力：
1. **知识库问答**：通过 search_documents 工具搜索已上传的文档并基于文档内容回答问题
2. **时间查询**：通过 get_current_time 工具获取当前时间
3. **数学计算**：通过 calculate 工具进行数学运算

## 行为准则
- 当用户询问关于文档的内容时，**必须**先调用 search_documents 工具检索相关内容
- 回答时引用文档来源，保持准确性
- 如果知识库中没有相关信息，如实告知用户
- 使用中文回答，表达清晰、友好

## 格式要求
- 重要内容使用 **加粗** 标注
- 列表项使用 - 或数字
- 代码使用 ``` 包裹"""


def _build_agent():
    """每次调用构建 agent（绑定全局 memory checkpointer）"""
    llm = _build_llm()
    return create_react_agent(
        model=llm,
        tools=_TOOLS,
        prompt=SystemMessage(content=_SYSTEM_PROMPT),
        checkpointer=_memory,
    )


# ── 对外接口 ──────────────────────────────────────────────────────────────────

def _thread_config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


async def chat_stream(user_message: str, session_id: str) -> AsyncIterator[str]:
    """流式输出 Agent 响应"""
    agent = _build_agent()
    config = _thread_config(session_id)

    async for event in agent.astream_events(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
        version="v2",
    ):
        kind = event.get("event")

        if kind == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield chunk.content

        elif kind == "on_tool_start":
            tool_name = event.get("name", "")
            tool_input = event.get("data", {}).get("input", {})
            yield f"\n\n> 🔧 **调用工具**: `{tool_name}`\n> 输入: `{tool_input}`\n\n"


async def chat(user_message: str, session_id: str) -> str:
    """非流式 Agent 响应"""
    agent = _build_agent()
    config = _thread_config(session_id)

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
    )
    messages = result.get("messages", [])
    # 取最后一条 AI 消息
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


def clear_session(session_id: str) -> None:
    """清除会话历史（通过覆写空消息列表）"""
    # MemorySaver 不暴露 delete，通过写入空状态来重置
    try:
        _memory.put(
            {"configurable": {"thread_id": session_id}},
            None,
            {},
            {},
        )
    except Exception:
        pass


def get_session_messages(session_id: str) -> List[dict]:
    """获取会话历史消息"""
    try:
        checkpoint = _memory.get({"configurable": {"thread_id": session_id}})
        if not checkpoint:
            return []
        messages = checkpoint.get("channel_values", {}).get("messages", [])
        result = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                result.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                result.append({"role": "assistant", "content": content})
        return result
    except Exception:
        return []
