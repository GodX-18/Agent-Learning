# LangChain RAG 智能体应用

基于 LangChain 构建的 RAG 智能问答应用，支持文档上传、向量检索和多工具 Agent。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Python |
| AI 框架 | LangChain 0.3 |
| 向量数据库 | ChromaDB |
| 语言模型 | OpenAI GPT-4o-mini |
| 嵌入模型 | text-embedding-3-small |
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 样式 | Tailwind CSS |

## 功能特性

- **📄 RAG 文档问答**：上传 PDF/TXT/MD/DOCX，自动分块向量化，智能检索回答
- **🤖 LangChain Agent**：集成多工具（知识库搜索、时间查询、数学计算）
- **💬 流式输出**：SSE 实时流式返回 AI 响应
- **🧠 对话记忆**：维护多轮对话上下文
- **🎨 现代 UI**：深色主题，Markdown 渲染，代码高亮

## 快速开始

### 1. 配置 API Key

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 OpenAI API Key
```

### 2. 一键启动

```bash
./start.sh
```

### 3. 访问应用

- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs

## 手动启动

### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
learn-agent/
├── backend/
│   ├── main.py          # FastAPI 路由
│   ├── agent.py         # LangChain Agent + 工具
│   ├── rag_engine.py    # RAG 文档处理 + ChromaDB
│   ├── config.py        # 配置管理
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 主界面
│   │   ├── api.ts               # API 请求
│   │   └── components/
│   │       ├── MessageBubble.vue  # 消息气泡
│   │       └── DocumentPanel.vue  # 文档管理面板
│   └── package.json
└── start.sh             # 一键启动脚本
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/documents/upload` | 上传文档 |
| GET | `/documents` | 获取文档列表 |
| DELETE | `/documents/{id}` | 删除文档 |
| POST | `/chat` | 发送消息（支持流式） |
| GET | `/sessions/{id}` | 获取会话历史 |
| DELETE | `/sessions/{id}` | 清除会话 |
