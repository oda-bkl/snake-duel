def test_submit_score_authenticated(client, alice_token):
    r = client.post(
        "/api/scores",
        json={"mode": "walls", "score": 500},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 500
    assert body["mode"] == "walls"
    assert body["username"] == "alice"
    assert body["id"]
    assert body["createdAt"]


def test_submit_score_unauthenticated(client):
    r = client.post("/api/scores", json={"mode": "walls", "score": 100})
    assert r.status_code == 401


def test_leaderboard_walls(client):
    r = client.get("/api/scores/leaderboard?mode=walls")
    assert r.status_code == 200
    scores = r.json()
    assert len(scores) > 0
    # Verify descending order
    values = [s["score"] for s in scores]
    assert values == sorted(values, reverse=True)


def test_leaderboard_wrap(client):
    r = client.get("/api/scores/leaderboard?mode=wrap")
    assert r.status_code == 200
    scores = r.json()
    assert all(s["mode"] == "wrap" for s in scores)


def test_leaderboard_limit(client):
    r = client.get("/api/scores/leaderboard?mode=walls&limit=1")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_leaderboard_no_mode_is_422(client):
    r = client.get("/api/scores/leaderboard")
    assert r.status_code == 422


def test_submitted_score_appears_in_leaderboard(client, alice_token):
    client.post(
        "/api/scores",
        json={"mode": "walls", "score": 9999},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    r = client.get("/api/scores/leaderboard?mode=walls")
    top = r.json()[0]
    assert top["score"] == 9999
