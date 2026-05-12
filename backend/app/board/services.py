from __future__ import annotations

from app.db import get_connection


def list_board_dates() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT date FROM board_days ORDER BY date").fetchall()
    return [row["date"] for row in rows]


def create_board_day(date: str, title: str, focus: str, rationale: list[str] | None = None) -> dict:
    rationale = rationale or []
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO board_days (date, title, focus)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET title=excluded.title, focus=excluded.focus
            """,
            (date, title, focus),
        )
        conn.execute("DELETE FROM board_day_rationale WHERE day_date = ?", (date,))
        for index, content in enumerate(rationale, start=1):
            conn.execute(
                """
                INSERT INTO board_day_rationale (day_date, content, sort_order)
                VALUES (?, ?, ?)
                """,
                (date, content, index),
            )
        conn.commit()
    return get_board_day(date) or {"date": date, "title": title, "focus": focus, "tasks": []}


def get_board_day(date: str) -> dict | None:
    with get_connection() as conn:
        day = conn.execute(
            "SELECT date, title, focus FROM board_days WHERE date = ?",
            (date,),
        ).fetchone()
        if day is None:
            return None

        rationale_rows = conn.execute(
            """
            SELECT content
            FROM board_day_rationale
            WHERE day_date = ?
            ORDER BY sort_order
            """,
            (date,),
        ).fetchall()
        task_rows = conn.execute(
            """
            SELECT id, task_key, title, eta, done
            FROM board_tasks
            WHERE day_date = ?
            ORDER BY sort_order
            """,
            (date,),
        ).fetchall()

        tasks = []
        for task in task_rows:
            step_rows = conn.execute(
                """
                SELECT step_type, content
                FROM board_task_steps
                WHERE task_id = ?
                ORDER BY sort_order
                """,
                (task["id"],),
            ).fetchall()
            tasks.append(
                {
                    "id": task["id"],
                    "task_key": task["task_key"],
                    "title": task["title"],
                    "eta": task["eta"],
                    "how": [row["content"] for row in step_rows if row["step_type"] == "how"],
                    "criteria": [
                        row["content"] for row in step_rows if row["step_type"] == "criteria"
                    ],
                    "done": bool(task["done"]),
                }
            )

    return {
        "date": day["date"],
        "title": day["title"],
        "focus": day["focus"],
        "rationale": [row["content"] for row in rationale_rows],
        "tasks": tasks,
    }


def create_board_task(
    date: str,
    title: str,
    eta: str,
    how: list[str],
    criteria: list[str],
) -> dict | None:
    with get_connection() as conn:
        day = conn.execute("SELECT date FROM board_days WHERE date = ?", (date,)).fetchone()
        if day is None:
            return None

        next_order = conn.execute(
            """
            SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order
            FROM board_tasks
            WHERE day_date = ?
            """,
            (date,),
        ).fetchone()["next_order"]
        task_key = f"{date}-task-{next_order}"

        cursor = conn.execute(
            """
            INSERT INTO board_tasks (day_date, task_key, title, eta, done, sort_order)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (date, task_key, title, eta, next_order),
        )
        task_id = cursor.lastrowid

        _replace_steps(conn, task_id, "how", how)
        _replace_steps(conn, task_id, "criteria", criteria)
        conn.commit()

    return get_board_task(task_id)


def get_board_task(task_id: int) -> dict | None:
    with get_connection() as conn:
        task = conn.execute(
            """
            SELECT id, day_date, task_key, title, eta, done
            FROM board_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        if task is None:
            return None
        step_rows = conn.execute(
            """
            SELECT step_type, content
            FROM board_task_steps
            WHERE task_id = ?
            ORDER BY sort_order
            """,
            (task_id,),
        ).fetchall()

    return {
        "id": task["id"],
        "date": task["day_date"],
        "task_key": task["task_key"],
        "title": task["title"],
        "eta": task["eta"],
        "how": [row["content"] for row in step_rows if row["step_type"] == "how"],
        "criteria": [row["content"] for row in step_rows if row["step_type"] == "criteria"],
        "done": bool(task["done"]),
    }


def update_board_task(
    task_id: int,
    title: str | None = None,
    eta: str | None = None,
    how: list[str] | None = None,
    criteria: list[str] | None = None,
    done: bool | None = None,
) -> dict | None:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, title, eta, done FROM board_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if existing is None:
            return None

        conn.execute(
            """
            UPDATE board_tasks
            SET title = ?, eta = ?, done = ?
            WHERE id = ?
            """,
            (
                title if title is not None else existing["title"],
                eta if eta is not None else existing["eta"],
                (1 if done else 0) if done is not None else existing["done"],
                task_id,
            ),
        )
        if how is not None:
            _replace_steps(conn, task_id, "how", how)
        if criteria is not None:
            _replace_steps(conn, task_id, "criteria", criteria)
        conn.commit()

    return get_board_task(task_id)


def delete_board_task(task_id: int) -> bool:
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM board_tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            return False
        conn.execute("DELETE FROM board_tasks WHERE id = ?", (task_id,))
        conn.commit()
    return True


def _replace_steps(conn, task_id: int, step_type: str, contents: list[str]) -> None:
    conn.execute(
        "DELETE FROM board_task_steps WHERE task_id = ? AND step_type = ?",
        (task_id, step_type),
    )
    for index, content in enumerate(contents, start=1):
        conn.execute(
            """
            INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, step_type, content, index),
        )
