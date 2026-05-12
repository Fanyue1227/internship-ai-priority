# Architecture

## Goal

Build a RAG-enhanced Agent that plans AI internship preparation tasks from
evidence in job descriptions, notes, and technical documents.

## Modules

```text
knowledge -> retrieval and citation evidence
agent     -> tool registry and planning orchestration
board     -> persisted daily tasks
llm       -> model provider abstraction
api       -> FastAPI HTTP layer
```

## Request Flow

```text
User goal
  -> Agent plan endpoint
  -> search_knowledge tool
  -> knowledge retrieval
  -> recommended stack and evidence
  -> create board day / task tools
```

## Data

The first version uses SQLite only:

- `documents`
- `chunks`
- `board_days`
- `board_day_rationale`
- `board_tasks`
- `board_task_steps`

Vector search from the old RAG Lab can be added behind
`app.knowledge.retrieval.search_knowledge` without changing Agent tools.
