"""/singers API のテスト。"""

from fastapi.testclient import TestClient
from syrupy.assertion import SnapshotAssertion


def test_get_singers_200(client: TestClient, snapshot_json: SnapshotAssertion) -> None:
    response = client.get("/singers", params={})
    # AivisSpeech Engine では未実装 (501 Not Implemented を返す)
    assert response.status_code == 501
    return
    assert response.status_code == 200
    assert snapshot_json == response.json()
