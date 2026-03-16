def test_get_collection_empty(client, auth_headers):
    response = client.get("/collection/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_collection_no_auth(client):
    response = client.get("/collection/")
    assert response.status_code == 401

def test_add_to_collection_success(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 1,
        "status": "owned",
        "play_count": 3,
        "personal_rating": 8.5,
        "notes": "Great game"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["game_id"] == 1
    assert data["status"] == "owned"
    assert data["play_count"] == 3
    assert data["personal_rating"] == 8.5
    assert data["notes"] == "Great game"

def test_add_to_collection_no_auth(client):
    response = client.post("/collection/", json={
        "game_id": 1,
        "status": "owned"
    })
    assert response.status_code == 401


def test_add_to_collection_duplicate(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 1,
        "status": "owned"
    }, headers=auth_headers)
    assert response.status_code == 400
    assert "already in collection" in response.json()["detail"]

def test_add_to_collection_game_not_found(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 99999,
        "status": "owned"
    }, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

def test_add_to_collection_invalid_status(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 2,
        "status": "invalidstatus"
    }, headers=auth_headers)
    assert response.status_code == 422

def test_add_to_collection_invalid_rating_too_high(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 2,
        "status": "owned",
        "personal_rating": 11.0
    }, headers=auth_headers)
    assert response.status_code == 422

def test_add_to_collection_invalid_rating_too_low(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 2,
        "status": "owned",
        "personal_rating": 0.5
    }, headers=auth_headers)
    assert response.status_code == 422

def test_add_to_collection_negative_play_count(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 2,
        "status": "owned",
        "play_count": -1
    }, headers=auth_headers)
    assert response.status_code == 422

def test_add_to_collection_notes_too_long(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 2,
        "status": "owned",
        "notes": "x" * 501
    }, headers=auth_headers)
    assert response.status_code == 422

def test_add_to_collection_invalid_game_id(client, auth_headers):
    response = client.post("/collection/", json={
        "game_id": 0,
        "status": "owned"
    }, headers=auth_headers)
    assert response.status_code == 422

def test_get_collection_has_item(client, auth_headers):
    response = client.get("/collection/", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(item["game_id"] == 1 for item in results)

def test_patch_collection_item_success(client, auth_headers):
    # Get the collection to find the item id
    collection = client.get("/collection/", headers=auth_headers).json()
    item_id = next(item["id"] for item in collection if item["game_id"] == 1)

    response = client.patch(f"/collection/{item_id}", json={
        "play_count": 10,
        "personal_rating": 9.0,
        "status": "played"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["play_count"] == 10
    assert data["personal_rating"] == 9.0
    assert data["status"] == "played"

def test_patch_collection_partial_update(client, auth_headers):
    collection = client.get("/collection/", headers=auth_headers).json()
    item_id = next(item["id"] for item in collection if item["game_id"] == 1)

    response = client.patch(f"/collection/{item_id}", json={
        "play_count": 15
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["play_count"] == 15

def test_patch_collection_item_not_found(client, auth_headers):
    response = client.patch("/collection/99999", json={
        "play_count": 5
    }, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

def test_patch_collection_no_auth(client):
    response = client.patch("/collection/1", json={
        "play_count": 5
    })
    assert response.status_code == 401

def test_patch_collection_invalid_rating(client, auth_headers):
    collection = client.get("/collection/", headers=auth_headers).json()
    item_id = collection[0]["id"]

    response = client.patch(f"/collection/{item_id}", json={
        "personal_rating": 15.0
    }, headers=auth_headers)
    assert response.status_code == 422

def test_get_collection_stats_success(client, auth_headers):
    response = client.get("/collection/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_games" in data
    assert "status_breakdown" in data
    assert "average_complexity" in data
    assert "top_mechanics" in data
    assert "total_plays" in data

def test_get_collection_stats_no_auth(client):
    response = client.get("/collection/stats")
    assert response.status_code == 401

def test_get_collection_stats_values(client, auth_headers):
    response = client.get("/collection/stats", headers=auth_headers)
    data = response.json()
    assert data["total_games"] >= 1
    assert data["total_plays"] >= 0
    assert isinstance(data["top_mechanics"], list)
    assert isinstance(data["status_breakdown"], dict)

def test_get_collection_recommend_success(client, auth_headers):
    response = client.get("/collection/recommend", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

def test_get_collection_recommend_excludes_owned(client, auth_headers):
    collection = client.get("/collection/", headers=auth_headers).json()
    owned_ids = {item["game_id"] for item in collection}

    response = client.get("/collection/recommend", headers=auth_headers)
    results = response.json()
    recommended_ids = {g["id"] for g in results}

    assert owned_ids.isdisjoint(recommended_ids)

def test_get_collection_recommend_no_auth(client):
    response = client.get("/collection/recommend")
    assert response.status_code == 401

def test_delete_collection_item_success(client, auth_headers):
    # Add a fresh game to delete
    client.post("/collection/", json={
        "game_id": 2,
        "status": "wishlist"
    }, headers=auth_headers)

    collection = client.get("/collection/", headers=auth_headers).json()
    item_id = next(item["id"] for item in collection if item["game_id"] == 2)

    response = client.delete(f"/collection/{item_id}", headers=auth_headers)
    assert response.status_code == 204

def test_delete_collection_item_not_found(client, auth_headers):
    response = client.delete("/collection/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

def test_delete_collection_no_auth(client):
    response = client.delete("/collection/1")
    assert response.status_code == 401

def test_delete_removes_from_collection(client, auth_headers):
    # Add game 2 again since previous test deleted it
    client.post("/collection/", json={
        "game_id": 2,
        "status": "wishlist"
    }, headers=auth_headers)

    collection = client.get("/collection/", headers=auth_headers).json()
    item_id = next(item["id"] for item in collection if item["game_id"] == 2)

    client.delete(f"/collection/{item_id}", headers=auth_headers)

    collection_after = client.get("/collection/", headers=auth_headers).json()
    assert not any(item["game_id"] == 2 for item in collection_after)