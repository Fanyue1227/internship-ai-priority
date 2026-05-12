# Internship AI Priority

这是一个面向 AI 实习准备场景的岗位知识增强学习规划项目。

项目核心不是简单调用模型 API，而是围绕 `RAG + Tool Calling + 任务规划` 搭建一条完整链路，使系统能够：

- 检索岗位 JD、技术文档与学习笔记
- 基于知识库生成有依据的学习建议
- 调用工具创建、更新和管理每日任务

核心流程为：

```text
岗位文档 / 学习笔记 -> 知识切分与检索 -> RAG 问答 / Agent 工具调用 -> 每日任务规划
```

## 项目内容

本仓库当前包含：

- 基于 Markdown 的岗位知识库
- 文档切分、知识检索与回答生成
- FastAPI 后端接口
- 基于工具调用的任务规划流程
- 基于 SQLite 的数据持久化

## 目录结构

```text
backend/app/knowledge   文档切分、检索、回答生成
backend/app/board       任务看板 schema 与服务
backend/app/agent       规划逻辑与工具调用
backend/app/llm         模型提供方抽象
backend/app/api         FastAPI 路由
data/raw/jobs           岗位 JD 与原始文档
frontend                最小化交互前端
prompts                 提示词模板
```

## 环境准备

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 启动后端

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

常用地址：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/system/status
```

## 常用命令

构建知识库：

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\build_corpus.py
```

初始化任务看板：

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\seed_board.py
```

运行测试：

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -v
```

## 一个最小演示流程

1. `POST /api/knowledge/ingest`
2. `POST /api/agent/tools/execute` 调用 `search_knowledge`
3. `POST /api/board/days`
4. `POST /api/agent/tools/execute` 调用 `create_task`

