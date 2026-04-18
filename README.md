# 实习任务看板 API

一个用 FastAPI + SQLite 搭建的小项目，用来管理实习准备任务、展示任务看板，并通过模型 API 生成任务执行顺序建议。

## 运行

项目虚拟环境在上一级 `Python/.venv` 时：

```powershell
cd C:\Users\fanjk\Documents\obsidian\obsidian\实习\Python\internship-ai-priority
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

不激活虚拟环境也可以直接运行：

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 常用地址

```text
http://127.0.0.1:8000/          后端健康检查
http://127.0.0.1:8000/docs      FastAPI 自动接口文档
http://127.0.0.1:8000/board     任务看板页面
```

## 当前接口

```text
GET    /board/api/dates
GET    /board/api/days/{date}
POST   /board/api/tasks
PATCH  /board/api/tasks/{task_id}
DELETE /board/api/tasks/{task_id}
PATCH  /board/api/tasks/{task_id}/done
GET    /board/api/days/{date}/prompt-preview
POST   /board/api/days/{date}/ai-plan
```

## 调用示例

查看某天看板数据：

```powershell
curl http://127.0.0.1:8000/board/api/days/2026-04-17
```

预览发给模型的 prompt：

```powershell
curl http://127.0.0.1:8000/board/api/days/2026-04-17/prompt-preview
```

调用模型生成任务执行计划：

```powershell
curl -X POST http://127.0.0.1:8000/board/api/days/2026-04-17/ai-plan
```

跳过模型调用，直接使用规则版 fallback：

```powershell
curl -X POST "http://127.0.0.1:8000/board/api/days/2026-04-17/ai-plan?use_model=false"
```

## 目录结构

```text
app/main.py              应用入口，负责创建 FastAPI app、注册路由、返回前端页面
app/db.py                数据库路径和 SQLite 连接入口
app/schemas.py           看板接口的 Pydantic 请求体模型
app/board_services.py    任务看板 board_* 表的数据库读写
app/board_routes.py      任务看板 API
app/api_clients.py       模型 API 调用、看板 prompt、AI plan 和 fallback
data/app.db              SQLite 数据库
data/board_seed.json     看板初始数据备份
static/board.html        单文件前端页面
tests/                   看板服务和 AI plan 测试
```
