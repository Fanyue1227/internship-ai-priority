# Runbook

## Backend

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Build Corpus

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe scripts\build_corpus.py
```

## Seed Board

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe scripts\seed_board.py
```

## Verify

```powershell
cd C:\Users\fanjk\Desktop\实习\internship-agent-lab\backend
..\.venv\Scripts\python.exe -m pytest tests -v
```
