from pathlib import Path

from app.board.services import create_board_day, create_board_task, get_board_day
from app.db import configure_database, init_db


def test_creates_board_day_and_task(tmp_path: Path):
    configure_database(tmp_path / "data")
    init_db()

    create_board_day(
        date="2026-04-30",
        title="Day 1 - PyTorch",
        focus="Run a minimal training loop.",
        rationale=["PyTorch is required by target LLM roles."],
    )
    task = create_board_task(
        date="2026-04-30",
        title="跑通 PyTorch 训练闭环",
        eta="2 小时",
        how=["实现 Dataset/DataLoader", "完成 train/eval loop"],
        criteria=["脚本能输出训练 loss"],
    )

    day = get_board_day("2026-04-30")

    assert task is not None
    assert day is not None
    assert day["tasks"][0]["title"] == "跑通 PyTorch 训练闭环"
    assert day["tasks"][0]["how"] == ["实现 Dataset/DataLoader", "完成 train/eval loop"]
