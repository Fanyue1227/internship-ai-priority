from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.board_routes import router as board_router


app = FastAPI(
    title="实习任务管理 API",
    description="用 FastAPI、SQLite 和模型 API 管理实习准备任务。",
)

# Register route groups. main.py only assembles the app.
app.include_router(board_router)

BASE_DIR = Path(__file__).resolve().parents[1]
BOARD_HTML_PATH = BASE_DIR / "static" / "board.html"


@app.get("/board", include_in_schema=False)
@app.get("/board/", include_in_schema=False)
def read_board_page():
    """Return the single-file frontend page."""
    return FileResponse(BOARD_HTML_PATH)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "实习任务管理 API 运行中！"}
