"""动作接口共用出口：所有模块的动作端点走同一套解析与回执组装流程。

路由层只声明路径与文档，动作名从载荷最外层取、回执按统一结构组装，
都收在这里，避免各模块再各写一套。
"""
from __future__ import annotations

from typing import Any, Protocol

from app.schemas import ActionPayload, ActionResult


class ActionRunner(Protocol):
    """各模块 service 执行动作的统一签名。"""

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str, bool]: ...


def run_action_endpoint(service: ActionRunner, entry_id: int, payload: ActionPayload) -> ActionResult:
    """从载荷最外层取动作名，执行后按统一结构组装回执。"""
    action = payload.action.strip()
    entry, message, repeated = service.run_action(entry_id, action)
    if entry is None:
        return ActionResult(ok=False, message=message)
    return ActionResult(ok=True, message=message, entry=entry, repeated=repeated)
