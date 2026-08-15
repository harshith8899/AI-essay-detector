"""Small integration test for POST /analyze:

essay -> GPT-2 -> stylometry -> feature vector -> scaler -> classifier
      -> sentence evidence -> JSON response
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_ESSAY = (
    "I grew up in a small town where everyone knew everyone else. "
    "Moreover, this closeness plays a pivotal role in how I understand community. "
    "When I left for college, I finally understood what I had taken for granted."
)


def test_health_check_still_works():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "AI Essay Detector"}


def test_analyze_returns_200_with_expected_shape():
    resp = client.post("/analyze", json={"essay": SAMPLE_ESSAY})
    assert resp.status_code == 200

    data = resp.json()
    assert {"essay_score", "label", "sentences", "limitations"}.issubset(data.keys())

    assert isinstance(data["essay_score"], (int, float))
    assert isinstance(data["label"], str)

    assert len(data["sentences"]) == 3
    for sentence in data["sentences"]:
        assert "start_offset" in sentence and "end_offset" in sentence
        assert SAMPLE_ESSAY[sentence["start_offset"] : sentence["end_offset"]] == sentence["text"]
        assert isinstance(sentence["score"], (int, float))
        assert len(sentence["top_features"]) > 0
        for feature in sentence["top_features"]:
            assert {"name", "contribution", "plain_language_note"}.issubset(feature.keys())

    assert len(data["limitations"]) > 0
    assert all(isinstance(item, str) for item in data["limitations"])


def test_analyze_empty_essay_returns_4xx():
    resp = client.post("/analyze", json={"essay": ""})
    assert 400 <= resp.status_code < 500


def test_analyze_whitespace_only_essay_returns_4xx():
    resp = client.post("/analyze", json={"essay": "   \n\t  "})
    assert 400 <= resp.status_code < 500


def test_analyze_missing_field_returns_4xx():
    resp = client.post("/analyze", json={})
    assert 400 <= resp.status_code < 500
