import sqlite3
import unittest

from app.board_services import get_board_day, list_board_dates, update_board_task_done


class BoardServicesTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE board_days (
                date TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                focus TEXT NOT NULL
            );
            CREATE TABLE board_day_rationale (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT NOT NULL,
                content TEXT NOT NULL,
                sort_order INTEGER NOT NULL
            );
            CREATE TABLE board_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT NOT NULL,
                task_key TEXT NOT NULL,
                title TEXT NOT NULL,
                eta TEXT NOT NULL,
                done INTEGER NOT NULL,
                sort_order INTEGER NOT NULL
            );
            CREATE TABLE board_task_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                step_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sort_order INTEGER NOT NULL
            );
            """
        )
        cur.execute(
            "INSERT INTO board_days (date, title, focus) VALUES (?, ?, ?)",
            ("2026-04-16", "今日任务", "测试 focus"),
        )
        cur.execute(
            "INSERT INTO board_day_rationale (day_date, content, sort_order) VALUES (?, ?, ?)",
            ("2026-04-16", "测试 rationale", 1),
        )
        cur.execute(
            """
            INSERT INTO board_tasks (day_date, task_key, title, eta, done, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("2026-04-16", "task-a", "测试任务", "30 分钟", 0, 1),
        )
        task_id = cur.lastrowid
        cur.execute(
            "INSERT INTO board_task_steps (task_id, step_type, content, sort_order) VALUES (?, ?, ?, ?)",
            (task_id, "how", "第一步", 1),
        )
        cur.execute(
            "INSERT INTO board_task_steps (task_id, step_type, content, sort_order) VALUES (?, ?, ?, ?)",
            (task_id, "criteria", "达标标准", 1),
        )
        self.conn.commit()
        self.task_id = task_id

    def tearDown(self):
        self.conn.close()

    def test_list_board_dates(self):
        self.assertEqual(list_board_dates(self.conn), ["2026-04-16"])

    def test_get_board_day_returns_nested_data(self):
        day = get_board_day("2026-04-16", self.conn)

        self.assertEqual(day["date"], "2026-04-16")
        self.assertEqual(day["title"], "今日任务")
        self.assertEqual(day["rationale"], ["测试 rationale"])
        self.assertEqual(day["tasks"][0]["title"], "测试任务")
        self.assertEqual(day["tasks"][0]["how"], ["第一步"])
        self.assertEqual(day["tasks"][0]["criteria"], ["达标标准"])
        self.assertFalse(day["tasks"][0]["done"])

    def test_update_board_task_done(self):
        result = update_board_task_done(self.task_id, True, self.conn)
        day = get_board_day("2026-04-16", self.conn)

        self.assertTrue(result["done"])
        self.assertTrue(day["tasks"][0]["done"])


if __name__ == "__main__":
    unittest.main()
