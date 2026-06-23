import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

import store as st
from main import app


@pytest.fixture(autouse=True)
def fresh_store():
    st.reset_store()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def alice_token(client):
    r = client.post(
        "/api/auth/login", json={"username": "alice", "password": "password123"}
    )
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture
def bob_token(client):
    r = client.post("/api/auth/login", json={"username": "bob", "password": "letmein"})
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture
def alice_id(client):
    r = client.post(
        "/api/auth/login", json={"username": "alice", "password": "password123"}
    )
    return r.json()["user"]["id"]
