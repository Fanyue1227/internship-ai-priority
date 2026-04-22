import unittest
from unittest.mock import patch

from app import agent_tools


class AgentToolsTests(unittest.TestCase):
    def test_execute_tool_action_calls_allowed_tool(self):
        with patch.object(
            agent_tools,
            "update_board_task_done",
            return_value={"id": 10, "done": True},
        ) as update_done:
            result = agent_tools.execute_tool_action(
                "update_task_done",
                {"task_id": 10, "done": True},
            )

        update_done.assert_called_once_with(task_id=10, done=True)
        self.assertEqual(result, {"id": 10, "done": True})

    def test_execute_tool_action_rejects_unknown_tool(self):
        with self.assertRaises(ValueError):
            agent_tools.execute_tool_action("unknown_tool", {})


if __name__ == "__main__":
    unittest.main()
