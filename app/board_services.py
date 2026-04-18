from app.db import get_connection


def list_board_dates(conn=None):
    """Return all dates that have board data."""
    should_close = conn is None
    conn = conn or get_connection()

    rows = conn.execute("SELECT date FROM board_days ORDER BY date").fetchall()

    if should_close:
        conn.close()

    return [row["date"] for row in rows]


def get_board_day(date: str, conn=None):
    """Return one day's full board data as a nested structure for the frontend."""
    should_close = conn is None
    conn = conn or get_connection()

    day = conn.execute(
        "SELECT date, title, focus FROM board_days WHERE date = ?",
        (date,),
    ).fetchone()

    if day is None:
        if should_close:
            conn.close()
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
                "how": [
                    row["content"] for row in step_rows if row["step_type"] == "how"
                ],
                "criteria": [
                    row["content"]
                    for row in step_rows
                    if row["step_type"] == "criteria"
                ],
                "done": bool(task["done"]),
            }
        )

    result = {
        "date": day["date"],
        "title": day["title"],
        "focus": day["focus"],
        "rationale": [row["content"] for row in rationale_rows],
        "tasks": tasks,
    }

    if should_close:
        conn.close()

    return result


def update_board_task_done(task_id: int, done: bool, conn=None):
    """Persist a board task done state and return the updated task summary."""
    should_close = conn is None
    conn = conn or get_connection()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE board_tasks SET done = ? WHERE id = ?",
        (1 if done else 0, task_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        if should_close:
            conn.close()
        return None

    row = conn.execute(
        """
        SELECT id, task_key, title, eta, done
        FROM board_tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()

    result = {
        "id": row["id"],
        "task_key": row["task_key"],
        "title": row["title"],
        "eta": row["eta"],
        "done": bool(row["done"]),
    }

    if should_close:
        conn.close()

    return result

from app.db import get_connection


def list_board_dates(conn=None):
    """Return all dates that have board data."""
    should_close = conn is None
    conn = conn or get_connection()

    rows = conn.execute("SELECT date FROM board_days ORDER BY date").fetchall()

    if should_close:
        conn.close()

    return [row["date"] for row in rows]


def get_board_day(date: str, conn=None):
    """Return one day's full board data as a nested structure for the frontend."""
    should_close = conn is None
    conn = conn or get_connection()

    day = conn.execute(
        "SELECT date, title, focus FROM board_days WHERE date = ?",
        (date,),
    ).fetchone()

    if day is None:
        if should_close:
            conn.close()
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
                "how": [
                    row["content"] for row in step_rows if row["step_type"] == "how"
                ],
                "criteria": [
                    row["content"]
                    for row in step_rows
                    if row["step_type"] == "criteria"
                ],
                "done": bool(task["done"]),
            }
        )

    result = {
        "date": day["date"],
        "title": day["title"],
        "focus": day["focus"],
        "rationale": [row["content"] for row in rationale_rows],
        "tasks": tasks,
    }

    if should_close:
        conn.close()

    return result


def get_board_task_by_id(task_id: int, conn=None):
    """Return one board task with how/criteria lists."""
    should_close = conn is None
    conn = conn or get_connection()

    task = conn.execute(
        """
        SELECT id, day_date, task_key, title, eta, done
        FROM board_tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()

    if task is None:
        if should_close:
            conn.close()
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

    result = {
        "id": task["id"],
        "date": task["day_date"],
        "task_key": task["task_key"],
        "title": task["title"],
        "eta": task["eta"],
        "how": [row["content"] for row in step_rows if row["step_type"] == "how"],
        "criteria": [
            row["content"] for row in step_rows if row["step_type"] == "criteria"
        ],
        "done": bool(task["done"]),
    }

    if should_close:
        conn.close()

    return result


def update_board_task_done(task_id: int, done: bool, conn=None):
    """Persist a board task done state and return the updated task summary."""
    should_close = conn is None
    conn = conn or get_connection()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE board_tasks SET done = ? WHERE id = ?",
        (1 if done else 0, task_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        if should_close:
            conn.close()
        return None

    row = conn.execute(
        """
        SELECT id, task_key, title, eta, done
        FROM board_tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()

    result = {
        "id": row["id"],
        "task_key": row["task_key"],
        "title": row["title"],
        "eta": row["eta"],
        "done": bool(row["done"]),
    }

    if should_close:
        conn.close()

    return result

#CRUD里面的C
def create_board_task(date: str, title: str, eta: str, how: list[str], criteria: list[str], conn=None):
    """Create one board task and its steps."""
    should_close = conn is None
    conn = conn or get_connection()

#判断这一天的board是否存在，如果不存在，返回None，并关闭数据库连接
    try:
        day = conn.execute(
            "SELECT date FROM board_days WHERE date = ?",
            (date,),
        ).fetchone()

        if day is None:
            if should_close:
                conn.close()
            return None

#获取这一天最大的sort_order，并加1，用作新任务的sort_order
#COALESCE()如果前面的值是 NULL，就改用后面的值。
        next_sort_order = conn.execute(
            """
            SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order
            FROM board_tasks
            WHERE day_date = ?
            """,
            (date,),
        ).fetchone()["next_order"]

        task_key = f"{date}-task-{next_sort_order}"#通常是给业务层、前端、调试时更好认的标识

#必须先插入board_tasks，才能插入board_task_steps，因为board_task_steps依赖task_id，
#而tasks可以根据日期和sort_order来排序，然后再得到task_id
#cursor.lastrowid 的意思是：刚刚插入这一行后数据库给它分配的主键 id
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO board_tasks (day_date, task_key, title, eta, done, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (date, task_key, title, eta, 0, next_sort_order),
        )
        task_id = cursor.lastrowid

#enumerate()在遍历一个列表时，同时拿到“下标”和“元素”。
#这里的content是for的时候定义的临时变量
        for i, content in enumerate(how, start=1):
            cursor.execute(
                """
                INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, "how", content, i),
            )

        for i, content in enumerate(criteria, start=1):
            cursor.execute(
                """
                INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, "criteria", content, i),
            )

        conn.commit()
        result = get_board_task_by_id(task_id, conn=conn)

        if should_close:
            conn.close()

        return result

    except Exception:
        conn.rollback()#回滚可以保证数据的一致性，如果插入失败，就回滚到插入之前
        if should_close:
            conn.close()
        raise

#CRUD的R已经有了，现在是U
def update_board_task(
    task_id: int,
    title: str | None = None,
    eta: str | None = None,
    how: list[str] | None = None,
    criteria: list[str] | None = None,
    done: bool | None = None,
    conn=None,
):
    """Update one board task, supporting partial updates."""
    should_close = conn is None
    conn = conn or get_connection()

#先抓取这些数据，因为有可能只改其中一个，但是下面写的是四个一起更新
#分开更新的话可以不用先抓取，但是要先判断哪个不是None，然后更新哪个
    try:
        existing = conn.execute(
            """
            SELECT id, title, eta, done
            FROM board_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        if existing is None:
            if should_close:
                conn.close()
            return None

        new_title = title if title is not None else existing["title"]
        new_eta = eta if eta is not None else existing["eta"]
        new_done = (1 if done else 0) if done is not None else existing["done"]

        conn.execute(
            """
            UPDATE board_tasks
            SET title = ?, eta = ?, done = ?
            WHERE id = ?
            """,
            (new_title, new_eta, new_done, task_id),
        )

#这里先删后插入，是因为传入的how是列表，一条条比对是否要更新更麻烦。
        if how is not None:
            conn.execute(
                """
                DELETE FROM board_task_steps
                WHERE task_id = ? AND step_type = 'how'
                """,
                (task_id,),
            )
            for i, content in enumerate(how, start=1):
                conn.execute(
                    """
                    INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, "how", content, i),
                )
#同上
        if criteria is not None:
            conn.execute(
                """
                DELETE FROM board_task_steps
                WHERE task_id = ? AND step_type = 'criteria'
                """,
                (task_id,),
            )
            for i, content in enumerate(criteria, start=1):
                conn.execute(
                    """
                    INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, "criteria", content, i),
                )

        conn.commit()
        result = get_board_task_by_id(task_id, conn=conn)

        if should_close:
            conn.close()

        return result

    except Exception:
        conn.rollback()
        if should_close:
            conn.close()
        raise

#CRUD的D，代码很简单没啥好看的
def delete_board_task(task_id: int, conn=None):
    """Delete one board task and its related steps."""
    should_close = conn is None
    conn = conn or get_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM board_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            if should_close:
                conn.close()
            return False

        conn.execute(
            "DELETE FROM board_task_steps WHERE task_id = ?",
            (task_id,),
        )
        conn.execute(
            "DELETE FROM board_tasks WHERE id = ?",
            (task_id,),
        )

        conn.commit()

        if should_close:
            conn.close()

        return True

    except Exception:
        conn.rollback()
        if should_close:
            conn.close()
        raise