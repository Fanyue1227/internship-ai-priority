from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.board.services import create_board_day, create_board_task
from app.db import init_db


def main() -> None:
    init_db()
    create_board_day(
        date="2026-04-30",
        title="Day 1 - Python + PyTorch + Hugging Face",
        focus="Build the first model-foundation study day.",
        rationale=[
            "Target roles repeatedly mention Python, PyTorch, Hugging Face, LLM basics, Agent, and deployment.",
        ],
    )
    create_board_task(
        date="2026-04-30",
        title="跑通 PyTorch 训练闭环",
        eta="2 小时",
        how=[
            "实现 Dataset / DataLoader。",
            "实现 nn.Module、loss、optimizer、train/eval loop。",
            "记录 loss 和 eval 指标。",
        ],
        criteria=[
            "训练脚本能完整运行。",
            "能说明 Dataset、DataLoader、Model、Loss、Optimizer 各自职责。",
        ],
    )
    print("seeded board day 2026-04-30")


if __name__ == "__main__":
    main()
