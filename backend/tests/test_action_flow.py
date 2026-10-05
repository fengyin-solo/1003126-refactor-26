"""动作链路回归测试：统一载荷、统一回执、幂等与各入口数据一致。

覆盖这次整改的共用流程：
- 动作名放在请求体最外层，20 个模块都能执行成功；
- 回执结构统一为 {ok, message, entry, repeated}；
- 同一个动作重复提交只生效一次；
- 动作成功后列表、详情、运营概览读到同一份最新数据；
- 登记、筛选、分页等其它入口行为不变。
"""
from __future__ import annotations

import copy
import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store

MODULES = [
    "minearea", "gas", "ventilation", "roof", "waterhazard",
    "rockburst", "personnel", "dust", "fireprevent", "belt",
    "hoist", "power", "rescue", "training", "shift",
    "explosive", "roadway", "monitorstation", "certificate", "emergencydrill",
]

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_store():
    """每个用例跑完都还原数据，旧记录按当时的结果保留，互不影响。"""
    snapshot = copy.deepcopy(store._tables)
    yield
    store._tables = snapshot


def action_rules(module: str) -> dict[str, str]:
    return importlib.import_module(f"app.services.{module}").ACTION_RULES


def test_action_payload_at_top_level_takes_effect():
    """页面把动作名放在请求体最外层，后端按同一份约定解析。"""
    resp = client.post("/api/gas/1/actions", json={"action": "处置确认"})
    assert resp.status_code == 200
    receipt = resp.json()
    assert receipt["ok"] is True
    assert receipt["message"] == "瓦斯测点已处置确认"
    assert receipt["repeated"] is False
    assert receipt["entry"]["status"] == "已处置"
    assert receipt["entry"]["pending"] is False


@pytest.mark.parametrize("module", MODULES)
def test_all_modules_share_one_receipt_shape(module: str):
    """20 个模块的动作回执都按同一份结构返回。"""
    rules = action_rules(module)
    action, target = next(iter(rules.items()))
    resp = client.post(f"/api/{module}/1/actions", json={"action": action})
    assert resp.status_code == 200
    receipt = resp.json()
    assert set(receipt) == {"ok", "message", "entry", "repeated"}
    assert receipt["ok"] is True
    assert receipt["message"]
    assert receipt["entry"]["status"] == target


def test_repeat_same_action_only_takes_effect_once():
    """重复提交同一个动作：第一次生效，之后原样返回不再改动。"""
    first = client.post("/api/gas/1/actions", json={"action": "处置确认"}).json()
    assert first["repeated"] is False
    overview_after_first = client.get("/api/overview").json()

    second = client.post("/api/gas/1/actions", json={"action": "处置确认"}).json()
    assert second["ok"] is True
    assert second["repeated"] is True
    assert "不重复生效" in second["message"]
    assert second["entry"]["status"] == "已处置"

    overview_after_second = client.get("/api/overview").json()
    assert overview_after_first == overview_after_second


def test_list_detail_and_overview_read_same_fresh_data():
    """动作成功后，列表、详情、运营概览读到同一份最新数据。"""
    client.post("/api/gas/2/actions", json={"action": "超限报警"})

    detail = client.get("/api/gas/2").json()
    assert detail["status"] == "超限报警"
    assert detail["pending"] is True

    listing = client.get("/api/gas").json()
    row = next(item for item in listing["items"] if item["id"] == 2)
    assert row["status"] == detail["status"]
    assert row["pending"] == detail["pending"]

    overview = client.get("/api/overview").json()
    gas_card = next(item for item in overview["modules"] if item["name"] == "gas")
    all_rows = client.get("/api/gas?size=200").json()["items"]
    assert gas_card["pending"] == sum(1 for item in all_rows if item["pending"])
    assert gas_card["abnormal"] == sum(1 for item in all_rows if item["abnormal"])


def test_unknown_action_is_rejected_with_readable_message():
    receipt = client.post("/api/gas/1/actions", json={"action": "不存在的动作"}).json()
    assert receipt["ok"] is False
    assert receipt["entry"] is None
    assert "不属于瓦斯监测可执行范围" in receipt["message"]


def test_missing_entry_is_rejected():
    receipt = client.post("/api/gas/9999/actions", json={"action": "处置确认"}).json()
    assert receipt["ok"] is False
    assert "不存在或已归档" in receipt["message"]


def test_empty_action_is_rejected():
    receipt = client.post("/api/gas/1/actions", json={}).json()
    assert receipt["ok"] is False
    assert "不属于" in receipt["message"]


def test_other_entries_behavior_unchanged():
    """登记、筛选、分页上限等其它入口保持原有行为。"""
    missing = client.post("/api/gas", json={"values": {}}).json()
    assert missing["ok"] is False
    assert "缺少必填字段" in missing["message"]

    created = client.post(
        "/api/gas",
        json={"values": {"测点编号": "GAS-9001", "所在区域": "一采区", "瓦斯浓度": "0.4%"}},
    ).json()
    assert created["ok"] is True
    assert created["entry"]["status"] == "正常"

    filtered = client.get("/api/gas", params={"keyword": "GAS-9001"}).json()
    assert filtered["total"] == 1

    assert client.get("/api/gas", params={"size": 201}).status_code == 400
