"""Integration tests: full user flows against a real SQLite file database."""

from fastapi.testclient import TestClient


def _signup(client: TestClient, username: str, password: str) -> dict:
    r = client.post("/api/auth/signup", json={"username": username, "password": password})
    assert r.status_code == 201
    return r.json()


def _login(client: TestClient, username: str, password: str) -> dict:
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Core flow
# ---------------------------------------------------------------------------

def test_signup_creates_account_and_returns_token(client: TestClient):
    data = _signup(client, "alice", "hunter2")
    assert data["user"]["username"] == "alice"
    assert data["token"].startswith("t_")
    assert data["user"]["id"].startswith("u_")


def test_login_returns_valid_session(client: TestClient):
    _signup(client, "alice", "hunter2")
    data = _login(client, "alice", "hunter2")
    assert data["user"]["username"] == "alice"
    assert data["token"].startswith("t_")


def test_submit_score_and_read_from_leaderboard(client: TestClient):
    token = _signup(client, "alice", "hunter2")["token"]

    r = client.post("/api/scores", json={"mode": "walls", "score": 42}, headers=_auth(token))
    assert r.status_code == 201
    score_id = r.json()["id"]
    assert r.json()["username"] == "alice"

    r2 = client.get("/api/leaderboard?mode=walls")
    assert r2.status_code == 200
    ids = [e["id"] for e in r2.json()]
    assert score_id in ids


def test_full_flow_signup_login_score_leaderboard(client: TestClient):
    """Happy-path end-to-end: sign up → log in → submit score → leaderboard."""
    _signup(client, "bob", "secret")
    login_token = _login(client, "bob", "secret")["token"]

    r = client.post(
        "/api/scores",
        json={"mode": "wrap", "score": 99},
        headers=_auth(login_token),
    )
    assert r.status_code == 201
    score_id = r.json()["id"]

    leaderboard = client.get("/api/leaderboard?mode=wrap").json()
    assert leaderboard[0]["id"] == score_id
    assert leaderboard[0]["score"] == 99
    assert leaderboard[0]["username"] == "bob"


# ---------------------------------------------------------------------------
# Persistence & isolation
# ---------------------------------------------------------------------------

def test_score_persists_after_logout_and_login(client: TestClient):
    """Score written in one session is visible after logging out and back in."""
    token = _signup(client, "carol", "pw")["token"]
    client.post("/api/scores", json={"mode": "walls", "score": 55}, headers=_auth(token))
    client.post("/api/auth/logout", headers=_auth(token))

    new_token = _login(client, "carol", "pw")["token"]
    leaderboard = client.get("/api/leaderboard?mode=walls").json()
    assert any(e["score"] == 55 and e["username"] == "carol" for e in leaderboard)

    # Confirm new token is valid
    r = client.get("/api/auth/session", headers=_auth(new_token))
    assert r.json()["user"]["username"] == "carol"


def test_leaderboard_sorted_highest_first(client: TestClient):
    token = _signup(client, "dave", "pw")["token"]
    for score in [10, 50, 30, 80, 20]:
        client.post("/api/scores", json={"mode": "walls", "score": score}, headers=_auth(token))

    scores = [e["score"] for e in client.get("/api/leaderboard?mode=walls").json()]
    assert scores == sorted(scores, reverse=True)


def test_scores_isolated_by_mode(client: TestClient):
    token = _signup(client, "eve", "pw")["token"]
    client.post("/api/scores", json={"mode": "walls", "score": 10}, headers=_auth(token))
    client.post("/api/scores", json={"mode": "wrap", "score": 20}, headers=_auth(token))

    walls = client.get("/api/leaderboard?mode=walls").json()
    wrap = client.get("/api/leaderboard?mode=wrap").json()
    assert all(e["mode"] == "walls" for e in walls)
    assert all(e["mode"] == "wrap" for e in wrap)


def test_multiple_users_leaderboard_ordering(client: TestClient):
    for username, score in [("u1", 30), ("u2", 70), ("u3", 50)]:
        token = _signup(client, username, "pw")["token"]
        client.post("/api/scores", json={"mode": "walls", "score": score}, headers=_auth(token))

    leaderboard = client.get("/api/leaderboard?mode=walls").json()
    scores = [e["score"] for e in leaderboard]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 70
