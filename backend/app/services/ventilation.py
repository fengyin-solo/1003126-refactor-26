"""通风系统业务规则：状态流转、字段校验与筛选口径都收在这里。"""
from __future__ import annotations

from typing import Any

from app.services.common import run_action_flow
from app.store import store

MODULE = "ventilation"
REQUIRED_FIELDS = ["设备编号", "设备类型", "额定风量"]
STATUS_ORDER = ["正常", "降频运行", "故障停机", "已更换"]
ACTION_RULES = {"降频运行": "降频运行", "故障停机": "故障停机", "办理更换": "已更换"}
NEGATIVE_ACTIONS = []


class VentilationService:
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
            rows = [row for row in rows if keyword in str(row.get("设备编号", ""))]
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
            entry_label="通风设备",
            module_label="通风系统",
        )
