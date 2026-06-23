GAME_PAYLOAD = {
    "userId": "placeholder",  # overwritten per test
    "mode": "walls",
    "score": 0,
    "snake": [{"x": 5, "y": 5}],
    "food": {"x": 8, "y": 8},
    "gridSize": 20,
    "alive": True,
}


def test_list_active_games_has_seed_data(client):
    r = client.get("/api/games/active")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_list_active_games_is_public(client):
    r = client.get("/api/games/active")
    assert r.status_code == 200


def test_upsert_creates_new_game(client, alice_token, alice_id):
    payload = {**GAME_PAYLOAD, "userId": alice_id}
    r = client.post(
        "/api/games/active",
        json=payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"]
    assert body["username"] == "alice"
    assert body["alive"] is True


def test_upsert_updates_existing_game(client, alice_token, alice_id):
    payload = {**GAME_PAYLOAD, "userId": alice_id}
    r1 = client.post(
        "/api/games/active",
        json=payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    gid = r1.json()["id"]

    r2 = client.post(
        "/api/games/active",
        json={**payload, "id": gid, "score": 100},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r2.status_code == 200
    assert r2.json()["score"] == 100
    assert r2.json()["id"] == gid


def test_upsert_requires_auth(client):
    r = client.post("/api/games/active", json=GAME_PAYLOAD)
    assert r.status_code == 401


def test_get_active_game(client, alice_token, alice_id):
    payload = {**GAME_PAYLOAD, "userId": alice_id}
    gid = client.post(
        "/api/games/active",
        json=payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    ).json()["id"]

    r = client.get(f"/api/games/active/{gid}")
    assert r.status_code == 200
    assert r.json()["id"] == gid


def test_get_active_game_missing_returns_null(client):
    r = client.get("/api/games/active/nonexistent")
    assert r.status_code == 200
    assert r.json() is None


def test_end_game(client, alice_token, alice_id):
    payload = {**GAME_PAYLOAD, "userId": alice_id}
    gid = client.post(
        "/api/games/active",
        json=payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    ).json()["id"]

    r = client.post(
        f"/api/games/active/{gid}/end",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 204

    assert client.get(f"/api/games/active/{gid}").json() is None


def test_end_game_not_found(client, alice_token):
    r = client.post(
        "/api/games/active/ghost/end",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 404


def test_end_game_requires_auth(client):
    r = client.post("/api/games/active/anything/end")
    assert r.status_code == 401
