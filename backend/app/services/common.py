"""动作流转共用流程：所有模块的状态流转、回执口径与幂等规则都收在这里。

各模块的 service 只提供自己的动作表、状态序列与叫法，流转逻辑一律走
run_action_flow，保证 20 个模块的处置行为完全一致。
"""
from __future__ import annotations

from typing import Any

from app.store import store


def run_action_flow(
    *,
    module: str,
    entry_id: int,
    action: str,
    rules: dict[str, str],
    status_order: list[str],
    negative_actions: list[str],
    entry_label: str,
    module_label: str,
) -> tuple[dict[str, Any] | None, str, bool]:
    """执行一次动作，返回 (记录, 回执说明, 是否重复提交)。

    记录为 None 表示执行失败（记录不存在、动作不在可执行范围等）。
    同一个动作重复提交时只生效一次：记录已处于目标状态的，直接返回
    当前记录并标记 repeated=True，不再改动任何字段。
    """
    entry = store.find(module, entry_id)
    if entry is None:
        return None, f"{entry_label} {entry_id} 不存在或已归档", False
    if action not in rules:
        return None, f"动作「{action}」不属于{module_label}可执行范围", False
    target = rules[action]
    if target not in status_order:
        return None, f"目标状态「{target}」不在允许的状态序列里", False
    if entry.get("status") == target:
        return entry, f"{entry_label}已处于「{target}」，动作「{action}」不重复生效", True
    entry["status"] = target
    entry["pending"] = target != status_order[-1]
    entry["abnormal"] = action in negative_actions
    return entry, f"{entry_label}已{action}", False
