"""动作链路共用流程：解析动作载荷、幂等执行、按统一结构发回执。

所有业务模块的动作接口都走这里，保证请求解析、回执结构、幂等口径全平台只有一份。
"""
from __future__ import annotations

from typing import Any, Protocol

from app.schemas import ActionPayload, ActionReceipt
from app.store import store


class SupportsRunAction(Protocol):
    """各模块 service 的动作执行接口：返回（记录或 None, 说明文案）。"""

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]: ...


def run_entry_action(service: SupportsRunAction, entry_id: int, payload: ActionPayload) -> ActionReceipt:
    """对单条记录执行动作并给出统一回执。

    同一 request_id 重复到达（重试、双击、网络重发）时不再执行，
    按当时落账的回执原样返回并标记 replayed，保证同一提交只生效一次。
    """
    action = payload.action_name()
    request_id = (payload.request_id or "").strip() or None
    if request_id:
        recorded = store.find_action_receipt(request_id)
        if recorded is not None:
            return ActionReceipt(**{**recorded, "replayed": True})
    entry, message = service.run_action(entry_id, action)
    receipt = ActionReceipt(
        ok=entry is not None,
        action=action,
        message=message,
        status=str(entry.get("status")) if entry is not None else None,
        entry=entry,
        request_id=request_id,
    )
    if request_id:
        store.record_action_receipt(request_id, receipt.model_dump())
    return receipt
