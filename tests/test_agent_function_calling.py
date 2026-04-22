import unittest
from unittest.mock import patch

from app import api_clients


class AgentFunctionCallingTests(unittest.TestCase):
    def test_extract_deepseek_tool_call_returns_confirmation_action(self):
        data = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "update_task_done",
                                    "arguments": '{"task_id": 290, "done": true}',
                                },
                            }
                        ],
                    }
                }
            ]
        }

        action = api_clients.extract_deepseek_tool_action(data)

        self.assertEqual(action["tool_call_id"], "call_1")
        self.assertEqual(action["tool_name"], "update_task_done")
        self.assertEqual(action["arguments"], {"task_id": 290, "done": True})
        self.assertTrue(action["requires_confirmation"])

    def test_get_agent_tool_proposal_uses_native_tools_payload(self):
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "update_task_done",
                                    "arguments": '{"task_id": 290, "done": true}',
                                },
                            }
                        ],
                    }
                }
            ]
        }

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return response_data

        with patch.object(
            api_clients,
            "get_model_config",
            return_value={
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "api_url": "https://example.test/chat",
                "api_token": "token",
            },
        ):
            with patch.object(api_clients, "requests") as requests_mock:
                requests_mock.post.return_value = FakeResponse()
                result = api_clients.get_agent_tool_proposal(
                    date="2026-04-20",
                    message="把 SQL 任务标记为完成",
                    day={"date": "2026-04-20", "tasks": []},
                )

        payload = requests_mock.post.call_args.kwargs["json"]
        self.assertIn("tools", payload)
        self.assertEqual(payload["tool_choice"], "auto")
        self.assertEqual(result["action"]["tool_name"], "update_task_done")
        self.assertTrue(result["requires_confirmation"])


if __name__ == "__main__":
    unittest.main()
