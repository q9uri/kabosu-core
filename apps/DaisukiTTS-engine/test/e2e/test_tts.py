"""TTSのテスト。"""

from fastapi.testclient import TestClient
from syrupy.assertion import SnapshotAssertion

# from test.utility import hash_wave_floats_from_wav_bytes


def test_テキストとキャラクターIDから音声を合成できる(
    client: TestClient, snapshot: SnapshotAssertion
) -> None:
    # テキストとキャラクター ID から AudioQuery を生成する
    audio_query_res = client.post(
        "/audio_query", params={"text": "テストです", "speaker": 888753760}
    )
    audio_query = audio_query_res.json()

    # AudioQuery から音声波形を生成する
    synthesis_res = client.post(
        "/synthesis", params={"speaker": 888753760}, json=audio_query
    )

    # リクエストが成功している
    assert synthesis_res.status_code == 200

    # FileResponse 内の .wav から抽出された音声波形が一致する
    assert synthesis_res.headers["content-type"] == "audio/wav"
    # AivisSpeech Engine の音声合成は常にある程度のランダム性があるため、テストではハッシュ値の比較は行わない
    # assert snapshot == hash_wave_floats_from_wav_bytes(synthesis_res.read())
