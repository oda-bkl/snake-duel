def test_signup_creates_session(client):
    r = client.post(
        "/api/auth/signup", json={"username": "newuser", "password": "pass1"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["username"] == "newuser"
    assert body["token"]


def test_signup_duplicate_username(client):
    client.post("/api/auth/signup", json={"username": "dup", "password": "p"})
    r = client.post("/api/auth/signup", json={"username": "dup", "password": "p"})
    assert r.status_code == 400


def test_login_valid_credentials(client):
    r = client.post(
        "/api/auth/login", json={"username": "alice", "password": "password123"}
    )
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "alice"
    assert r.json()["token"]


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401


def test_session_returns_user(client, alice_token):
    r = client.get(
        "/api/auth/session", headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "alice"


def test_session_without_token_returns_null(client):
    r = client.get("/api/auth/session")
    assert r.status_code == 200
    assert r.json() is None


def test_logout_invalidates_token(client, alice_token):
    r = client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert r.status_code == 204

    r2 = client.get(
        "/api/auth/session", headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert r2.json() is None


def test_logout_without_token_is_401(client):
    r = client.post("/api/auth/logout")
    assert r.status_code == 401
