import json
import os

import requests
from dotenv import load_dotenv
from app.agent_tools import describe_tool_action, get_agent_tool_definitions
from app.board_services import get_board_day


load_dotenv()


def get_model_config():
    """Read model provider configuration from environment variables."""
    provider = os.getenv("MODEL_PROVIDER")
    model_name = os.getenv("MODEL_NAME")
    api_url = os.getenv("MODEL_API_URL")
    api_token = os.getenv("MODEL_API_TOKEN")

    if not provider:
        raise ValueError("没有设置 MODEL_PROVIDER")
    if not model_name:
        raise ValueError("没有设置 MODEL_NAME")
    if not api_url:
        raise ValueError("没有设置 MODEL_API_URL")
    if not api_token:
        raise ValueError("没有设置 MODEL_API_TOKEN")

    provider = provider.lower()
    if provider not in {"claude", "deepseek"}:
        raise ValueError("目前只支持 claude 或 deepseek")

    return {
        "provider": provider,
        "model_name": model_name,
        "api_url": api_url,
        "api_token": api_token,
    }


def build_model_request(prompt: str):
    """Build provider-specific request headers and payload."""
    config = get_model_config()
    provider = config["provider"]
    model_name = config["model_name"]
    api_token = config["api_token"]

    if provider == "claude":
        headers = {
            "x-api-key": api_token,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model_name,
            "max_tokens": 1024,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        response_type = "claude"
    else:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个任务安排助手。你只能返回合法 JSON，不要输出任何额外文字。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "stream": False,
        }
        response_type = "deepseek"

    return {
        "api_url": config["api_url"],
        "headers": headers,
        "payload": payload,
        "response_type": response_type,
    }


def extract_model_text(data: dict, response_type: str) -> str:
    """Extract text from Claude or DeepSeek compatible responses."""
    if response_type == "claude":
        try:
            content_blocks = data["content"]
            text_parts = [
                block.get("text", "")
                for block in content_blocks
                if block.get("type") == "text"
            ]
            text = "".join(text_parts).strip()
            if not text:
                raise ValueError("Claude 返回里没有文本内容")
            return text
        except (KeyError, TypeError) as e:
            raise ValueError(f"Claude 返回格式不符合预期: {e}")

    try:
        text = data["choices"][0]["message"]["content"]
        if not text:
            raise ValueError("DeepSeek 返回里 content 为空")
        return text
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"DeepSeek 返回格式不符合预期: {e}")


def build_agent_messages(date: str, message: str, day: dict) -> list[dict]:
    """Build messages for provider-native task board tool calling."""
    board_json = json.dumps(day, ensure_ascii=False)
    return [
        {
            "role": "system",
            "content": (
                "You are a task board agent. Use the provided native tools when "
                "the user wants to create, update, complete, reopen, or delete a task. "
                "Only choose tools using task ids that appear in the board data. "
                "If the user only asks for advice or a summary, answer normally without a tool call. "
                "All write operations will be confirmed by the frontend before execution."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Board date: {date}\n"
                f"Current board data JSON:\n{board_json}\n\n"
                f"User command:\n{message}"
            ),
        },
    ]


def extract_deepseek_tool_action(data: dict) -> dict:
    """Extract the first OpenAI-compatible tool call from a DeepSeek response."""
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"DeepSeek tool response format is invalid: {e}") from e

    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        return {}

    tool_call = tool_calls[0]
    function = tool_call.get("function") or {}
    tool_name = function.get("name")
    raw_arguments = function.get("arguments") or "{}"

    if not tool_name:
        raise ValueError("DeepSeek tool call did not include function.name")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as e:
        raise ValueError("DeepSeek tool call arguments are not valid JSON") from e

    return {
        "tool_call_id": tool_call.get("id", ""),
        "tool_name": tool_name,
        "arguments": arguments,
        "requires_confirmation": True,
        "confirmation_text": describe_tool_action(tool_name, arguments),
    }


def get_agent_tool_proposal(date: str, message: str, day: dict | None = None) -> dict:
    """Ask the model for a provider-native tool call proposal."""
    config = get_model_config()
    if config["provider"] != "deepseek":
        raise ValueError("Native function calling is currently implemented for deepseek only")

    day = day if day is not None else get_board_day(date)
    if day is None:
        raise ValueError(f"Board day not found: {date}")

    payload = {
        "model": config["model_name"],
        "messages": build_agent_messages(date, message, day),
        "tools": get_agent_tool_definitions(),
        "tool_choice": "auto",
        "temperature": 0.1,
        "stream": False,
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        config["api_url"],
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError("Model API did not return valid JSON") from e

    action = extract_deepseek_tool_action(data)
    reply = data["choices"][0]["message"].get("content") or ""

    return {
        "ok": True,
        "source": "model",
        "provider": config["provider"],
        "model_name": config["model_name"],
        "reply": reply or ("请确认是否执行该操作。" if action else "没有需要执行的任务操作。"),
        "requires_confirmation": bool(action),
        "action": action or None,
    }


def build_board_day_task_lines(tasks: list[dict]) -> str:
    """把未完成的看板任务整理成模型更容易理解的中文文本。"""
    if not tasks:
        return "今天没有未完成任务。"

    task_blocks = []

    for i, task in enumerate(tasks, start=1):
        how_lines = "\n".join(
            [f"    - {step}" for step in task.get("how", [])]
        ) or "    - 无"

        criteria_lines = "\n".join(
            [f"    - {item}" for item in task.get("criteria", [])]
        ) or "    - 无"

        task_blocks.append(
            f"""任务 {i}
task_id: {task["id"]}
task_key: {task.get("task_key", "")}
标题: {task["title"]}
预计时间: {task["eta"]}
完成状态: 未完成
具体步骤:
{how_lines}
验收标准:
{criteria_lines}"""
        )

    return "\n\n".join(task_blocks)


def build_board_day_prompt(date: str) -> str:
    """把某一天的看板任务整理成模型可理解的 prompt。"""
    day = get_board_day(date)

    if day is None:
        raise ValueError(f"日期 {date} 不存在对应的看板数据")

    all_tasks = day.get("tasks", [])
    pending_tasks = [task for task in all_tasks if not task.get("done", False)]
    completed_tasks = [task for task in all_tasks if task.get("done", False)]

    rationale_lines = "\n".join(
        [f"- {item}" for item in day.get("rationale", [])]
    ) or "- 无"

    completed_lines = "\n".join(
        [f"- {task['title']}" for task in completed_tasks]
    ) or "- 无"

    pending_text = build_board_day_task_lines(pending_tasks)

    return f"""
你是一个任务安排助手。
下面是某一天的任务看板信息，请你根据任务内容安排一个合理的执行顺序。

日期：{day["date"]}
看板标题：{day.get("title", "")}
今日重点：{day.get("focus", "")}

安排背景：
{rationale_lines}

已完成任务（仅供背景参考，不需要再安排）：
{completed_lines}

未完成任务（你只能在这些任务里排序）：
{pending_text}

请根据以下因素综合排序：
1. 任务之间是否有前后依赖关系
2. 哪些任务更适合优先做，能更快推进整体进度
3. 预计时间是否合理，是否适合先完成短平快任务或先处理关键任务
4. 验收标准是否清晰，是否适合优先执行
5. 是否符合“今日重点”和“安排背景”

请严格返回合法 JSON，不要添加任何额外文字，不要输出 markdown 代码块，不要输出解释性前言。

返回格式如下：
{{
  "ordered_tasks": [
    {{
      "task_id": 0,
      "task_key": "示例-task-key",
      "title": "示例任务标题",
      "eta": "示例预计时间",
      "reason": "示例排序理由"
    }}
  ],
  "summary": "示例总体说明"
}}

如果今天没有未完成任务，请返回：
{{
  "ordered_tasks": [],
  "summary": "今天没有需要安排的未完成任务。"
}}
""".strip()


def build_board_day_rule_plan(date: str) -> dict:
    """在模型不可用时，按看板当前顺序生成一个可用的规则版安排。"""
    day = get_board_day(date)

    if day is None:
        raise ValueError(f"日期 {date} 不存在对应的看板数据")

    pending_tasks = [
        task for task in day.get("tasks", []) if not task.get("done", False)
    ]

    ordered_tasks = []
    for task in pending_tasks:
        ordered_tasks.append(
            {
                "task_id": task["id"],
                "task_key": task.get("task_key", ""),
                "title": task["title"],
                "eta": task["eta"],
                "reason": (
                    "按看板当前顺序执行；该任务仍未完成，且已经有明确的步骤和验收标准。"
                ),
            }
        )

    if not ordered_tasks:
        summary = "今天没有需要安排的未完成任务。"
    else:
        summary = (
            "模型暂时不可用，已按看板当前顺序返回未完成任务，"
            "保证后端仍能给出可执行安排。"
        )

    return {
        "ordered_tasks": ordered_tasks,
        "summary": summary,
    }


def get_board_day_ai_plan(
    date: str,
    use_fallback: bool = True,
    use_model: bool = True,
) -> dict:
    """调用模型为某一天的看板任务生成安排；失败时可自动降级到规则版安排。"""
    prompt = build_board_day_prompt(date)

    if not use_model:
        return {
            "ok": True,
            "source": "fallback",
            "fallback_reason": "use_model=false",
            "prompt": prompt,
            "plan": build_board_day_rule_plan(date),
        }

    try:
        req = build_model_request(prompt)

        response = requests.post(
            req["api_url"],
            headers=req["headers"],
            json=req["payload"],
            timeout=60,
        )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError as e:
            raise ValueError("模型 API 返回的不是合法 JSON") from e

        text = extract_model_text(data, req["response_type"])

        try:
            plan = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError("模型返回的内容不是合法 JSON") from e

        config = get_model_config()
        return {
            "ok": True,
            "source": "model",
            "provider": config["provider"],
            "model_name": config["model_name"],
            "prompt": prompt,
            "plan": plan,
        }
    except Exception as e:
        if not use_fallback:
            return {
                "ok": False,
                "source": "model",
                "error": str(e),
                "prompt": prompt,
            }

        return {
            "ok": True,
            "source": "fallback",
            "fallback_reason": str(e),
            "prompt": prompt,
            "plan": build_board_day_rule_plan(date),
        }
