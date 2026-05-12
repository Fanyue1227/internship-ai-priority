# Internship Agent Lab

Internship Agent Lab is a knowledge-grounded task planning project for AI internship preparation.

It combines:

- job-description retrieval
- evidence-based planning
- task board management
- tool-calling agent workflows

The core loop is:

```text
job docs / notes -> knowledge retrieval -> agent tools -> daily tasks
```

## What This Repo Contains

- Markdown-based job knowledge base
- chunking, retrieval, and answer generation
- FastAPI backend for knowledge, board, and agent routes
- tool-calling task planning workflow
- SQLite-based persistence
- a minimal frontend shell for local interaction

## Project Structure

```text
backend/app/knowledge   ingestion, chunking, retrieval
backend/app/board       task board schemas and services
backend/app/agent       planning logic and tools
backend/app/llm         provider abstraction
backend/app/api         FastAPI routers
data/raw/jobs           job description markdown files
frontend                minimal UI shell
prompts                 prompt templates
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run Backend

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Common URLs:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/system/status
```

## Useful Commands

Build knowledge base:

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\build_corpus.py
```

Seed board data:

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\seed_board.py
```

Run tests:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -v
```

## First Demo Flow

1. `POST /api/knowledge/ingest`
2. `POST /api/agent/tools/execute` with `search_knowledge`
3. `POST /api/board/days`
4. `POST /api/agent/tools/execute` with `create_task`

