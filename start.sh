#!/bin/bash
set -e

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 启动 LangChain RAG 智能体应用${NC}"
echo ""

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  未找到 backend/.env，正在从模板创建...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}📝 请编辑 backend/.env 填入你的 OpenAI API Key${NC}"
    echo ""
fi

# 安装后端依赖
echo -e "${GREEN}📦 安装后端依赖...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

# 启动后端
echo -e "${GREEN}🔧 启动后端服务 (port 8000)...${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 安装前端依赖
echo -e "${GREEN}📦 安装前端依赖...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# 启动前端
echo -e "${GREEN}🎨 启动前端服务 (port 5173)...${NC}"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ 应用已启动！${NC}"
echo -e "   前端: ${BLUE}http://localhost:5173${NC}"
echo -e "   后端 API: ${BLUE}http://localhost:8000${NC}"
echo -e "   API 文档: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
