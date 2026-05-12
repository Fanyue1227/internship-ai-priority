from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import init_db, get_data_dir
from app.knowledge.ingest import ingest_raw_documents


def main() -> None:
    init_db()
    summary = ingest_raw_documents(get_data_dir() / "raw")
    print(summary)


if __name__ == "__main__":
    main()
