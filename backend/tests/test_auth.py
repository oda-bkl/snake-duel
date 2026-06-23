import pytest
from fastapi.testclient import TestClient


def test_signup_creates_account(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": "bob", "password": "secret"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["username"] == "bob"
    assert body["token"].startswith("t_")


def test_signup_duplicate_username(client: TestClient):
    client.post("/api/auth/signup", json={"username": "bob", "password": "a"})
    r = client.post("/api/auth/signup", json={"username": "bob", "password": "b"})
    assert r.status_code == 409


def test_signup_case_insensitive_duplicate(client: TestClient):
    client.post("/api/auth/signup", json={"username": "Bob", "password": "a"})
    r = client.post("/api/auth/signup", json={"username": "bob", "password": "b"})
    assert r.status_code == 409


def test_login_success(client: TestClient):
    client.post("/api/auth/signup", json={"username": "carol", "password": "pw"})
    r = client.post("/api/auth/login", json={"username": "carol", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "carol"


def test_login_wrong_password(client: TestClient):
    client.post("/api/auth/signup", json={"username": "carol", "password": "pw"})
    r = client.post("/api/auth/login", json={"username": "carol", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user(client: TestClient):
    r = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401


def test_logout_invalidates_token(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    r = client.post("/api/auth/logout", headers=headers)
    assert r.status_code == 204
    # Token should no longer work
    r2 = client.post("/api/auth/logout", headers=headers)
    assert r2.status_code == 401


def test_logout_without_token(client: TestClient):
    r = client.post("/api/auth/logout")
    assert r.status_code == 401


def test_session_valid_token(client: TestClient, alice: dict):
    r = client.get("/api/auth/session", headers={"Authorization": f"Bearer {alice['token']}"})
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["username"] == "alice"


def test_session_no_token_returns_null(client: TestClient):
    r = client.get("/api/auth/session")
    assert r.status_code == 200
    assert r.json() is None


def test_session_invalid_token_returns_null(client: TestClient):
    r = client.get("/api/auth/session", headers={"Authorization": "Bearer t_bogus"})
    assert r.status_code == 200
    assert r.json() is None
