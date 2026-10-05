"""提升系统业务规则：状态流转、字段校验与筛选口径都收在这里。"""
from __future__ import annotations

from typing import Any

from app.services.common import run_action_flow
from app.store import store

MODULE = "hoist"
REQUIRED_FIELDS = ["提升机编号", "提升类型", "提升高度"]
STATUS_ORDER = ["正常", "钢丝绳磨损", "制动异常", "检修中"]
ACTION_RULES = {"磨损预警": "钢丝绳磨损", "制动检修": "制动异常", "探伤检测": "检修中"}
NEGATIVE_ACTIONS = []


class HoistService:
    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = store.rows(MODULE)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get("提升机编号", ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        total = len(rows)
        start = max(page - 1, 0) * size
        return rows[start:start + size], total

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        return store.find(MODULE, entry_id)

    def create_entry(self, values: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        missing = [field for field in REQUIRED_FIELDS if not str(values.get(field) or "").strip()]
        if missing:
            return None, missing
        rows = store.rows(MODULE)
        entry = {"id": max((int(row.get("id", 0)) for row in rows), default=0) + 1}
        entry.update({field: values.get(field) for field in REQUIRED_FIELDS})
        entry["status"] = STATUS_ORDER[0]
        entry["pending"] = True
        entry["abnormal"] = False
        rows.append(entry)
        return entry, []

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str, bool]:
        """执行动作：流转逻辑走共用流程，本模块只提供动作表与叫法。"""
        return run_action_flow(
            module=MODULE,
            entry_id=entry_id,
            action=action,
            rules=ACTION_RULES,
            status_order=STATUS_ORDER,
            negative_actions=NEGATIVE_ACTIONS,
            entry_label="提升机",
            module_label="提升系统",
        )
