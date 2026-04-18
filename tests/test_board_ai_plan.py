import unittest
import sys
import types
from unittest.mock import patch

requests_stub = types.SimpleNamespace(post=lambda *args, **kwargs: None)
dotenv_stub = types.SimpleNamespace(load_dotenv=lambda: None)
sys.modules.setdefault("requests", requests_stub)
sys.modules.setdefault("dotenv", dotenv_stub)

from app import api_clients


SAMPLE_DAY = {
    "date": "2026-04-17",
    "title": "Today",
    "focus": "Build board AI plan",
    "rationale": ["Use real board data"],
    "tasks": [
        {
            "id": 1,
            "task_key": "done-task",
            "title": "Finished task",
            "eta": "20 minutes",
            "how": ["Do old work"],
            "criteria": ["Old work is done"],
            "done": True,
        },
        {
            "id": 2,
            "task_key": "pending-a",
            "title": "Write prompt",
            "eta": "40 minutes",
            "how": ["Read board tasks", "Write clear prompt"],
            "criteria": ["Prompt includes task steps"],
            "done": False,
        },
        {
            "id": 3,
            "task_key": "pending-b",
            "title": "Return JSON plan",
            "eta": "30 minutes",
            "how": ["Call model", "Parse JSON"],
            "criteria": ["Response has ordered_tasks and summary"],
            "done": False,
        },
    ],
}


class BoardAiPlanTests(unittest.TestCase):
    def test_board_prompt_only_sends_pending_tasks_to_model(self):
        with patch.object(api_clients, "get_board_day", return_value=SAMPLE_DAY):
            prompt = api_clients.build_board_day_prompt("2026-04-17")

        self.assertIn("Write prompt", prompt)
        self.assertIn("Return JSON plan", prompt)
        self.assertIn("Finished task", prompt)
        self.assertIn("已完成任务", prompt)
        self.assertIn("ordered_tasks", prompt)
        self.assertIn("summary", prompt)

        pending_section = prompt.split("未完成任务")[1]
        self.assertNotIn("Finished task", pending_section)

    def test_rule_plan_returns_pending_tasks_in_board_order(self):
        with patch.object(api_clients, "get_board_day", return_value=SAMPLE_DAY):
            plan = api_clients.build_board_day_rule_plan("2026-04-17")

        self.assertEqual(
            [task["task_id"] for task in plan["ordered_tasks"]],
            [2, 3],
        )
        self.assertEqual(plan["ordered_tasks"][0]["task_key"], "pending-a")
        self.assertIn("summary", plan)

    def test_ai_plan_falls_back_when_model_config_is_unavailable(self):
        with patch.object(api_clients, "get_board_day", return_value=SAMPLE_DAY):
            with patch.object(
                api_clients,
                "build_model_request",
                side_effect=ValueError("missing model config"),
            ):
                result = api_clients.get_board_day_ai_plan("2026-04-17")

        self.assertTrue(result["ok"])
        self.assertEqual(result["source"], "fallback")
        self.assertEqual(
            [task["task_id"] for task in result["plan"]["ordered_tasks"]],
            [2, 3],
        )
        self.assertIn("missing model config", result["fallback_reason"])

    def test_ai_plan_can_skip_model_and_return_rule_plan_directly(self):
        with patch.object(api_clients, "get_board_day", return_value=SAMPLE_DAY):
            result = api_clients.get_board_day_ai_plan(
                "2026-04-17",
                use_model=False,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(result["source"], "fallback")
        self.assertEqual(result["fallback_reason"], "use_model=false")
        self.assertEqual(
            [task["task_id"] for task in result["plan"]["ordered_tasks"]],
            [2, 3],
        )


if __name__ == "__main__":
    unittest.main()
