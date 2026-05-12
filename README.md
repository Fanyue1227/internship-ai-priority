# Internship Agent Lab

RAG-enhanced task planning agent for AI internship preparation.

This project merges two earlier prototypes:

- Open Source RAG Lab: knowledge ingestion, retrieval, and citation-based answers.
- Internship AI Priority Board: board tasks, tool calling, and task execution.

The first integrated version focuses on a backend loop:

```text
job docs / notes -> knowledge search -> agent tools -> board tasks
```

## Structure

```text
backend/app/knowledge   Markdown ingestion, chunking, retrieval, answers
backend/app/board       Daily plan and task CRUD
backend/app/agent       Tool registry and evidence-based planning
backend/app/llm         Offline/Ollama provider abstraction
backend/app/api         FastAPI routers
data/raw/jobs           Job description markdown files
frontend                Minimal Vue shell
prompts                 Prompt templates
```

## Setup

Create a fresh Python environment, then install dependencies:

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `python` is not available on PATH, install Python first or point the command
to the actual `python.exe`.

## Run Backend

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Common URLs:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/system/status
```

## Build Knowledge Base

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe scripts\build_corpus.py
```

## Seed Board

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe scripts\seed_board.py
```

## Run Tests

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe -m pytest tests -v
```

## First API Flow

1. `POST /api/knowledge/ingest`
2. `POST /api/agent/tools/execute` with `search_knowledge`
3. `POST /api/board/days`
4. `POST /api/agent/tools/execute` with `create_task`
