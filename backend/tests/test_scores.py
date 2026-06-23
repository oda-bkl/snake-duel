from fastapi.testclient import TestClient


def test_submit_score(client: TestClient, auth_headers: dict):
    r = client.post("/api/scores", json={"mode": "walls", "score": 42}, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["score"] == 42
    assert body["mode"] == "walls"
    assert body["username"] == "alice"
    assert body["id"].startswith("s_")


def test_submit_score_unauthenticated(client: TestClient):
    r = client.post("/api/scores", json={"mode": "walls", "score": 10})
    assert r.status_code == 401


def test_leaderboard_empty(client: TestClient):
    r = client.get("/api/leaderboard?mode=walls")
    assert r.status_code == 200
    assert r.json() == []


def test_leaderboard_sorted(client: TestClient, auth_headers: dict):
    for score in [10, 50, 30]:
        client.post("/api/scores", json={"mode": "walls", "score": score}, headers=auth_headers)
    r = client.get("/api/leaderboard?mode=walls")
    scores = [e["score"] for e in r.json()]
    assert scores == sorted(scores, reverse=True)


def test_leaderboard_mode_filter(client: TestClient, auth_headers: dict):
    client.post("/api/scores", json={"mode": "walls", "score": 10}, headers=auth_headers)
    client.post("/api/scores", json={"mode": "wrap", "score": 20}, headers=auth_headers)
    walls = client.get("/api/leaderboard?mode=walls").json()
    wrap = client.get("/api/leaderboard?mode=wrap").json()
    assert all(e["mode"] == "walls" for e in walls)
    assert all(e["mode"] == "wrap" for e in wrap)


def test_leaderboard_limit(client: TestClient, auth_headers: dict):
    for i in range(5):
        client.post("/api/scores", json={"mode": "walls", "score": i * 10}, headers=auth_headers)
    r = client.get("/api/leaderboard?mode=walls&limit=3")
    assert len(r.json()) == 3
