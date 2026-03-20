def test_get_games_returns_results(client):
    response = client.get("/games/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_games_default_pagination(client):
    response = client.get("/games/")
    assert response.status_code == 200
    assert len(response.json()) <= 20

def test_get_games_custom_limit(client):
    response = client.get("/games/?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_games_offset(client):
    response_first = client.get("/games/?limit=1&offset=0")
    response_second = client.get("/games/?limit=1&offset=1")
    first = response_first.json()
    second = response_second.json()
    assert first[0]["id"] != second[0]["id"]


def test_get_games_search(client):
    response = client.get("/games/?search=Test Game One")
    assert response.status_code == 200
    results = response.json()
    assert any("Test Game One" in g["title"] for g in results)


def test_get_games_search_no_results(client):
    response = client.get("/games/?search=zzznomatchzzz")
    assert response.status_code == 200
    assert response.json() == []

def test_get_games_filter_by_mechanic(client):
    response = client.get("/games/?mechanic=Deck Construction")
    assert response.status_code == 200
    results = response.json()
    assert all("Deck Construction" in g["mechanics"] for g in results)


def test_get_games_filter_by_category(client):
    response = client.get("/games/?category=Strategy Games")
    assert response.status_code == 200
    results = response.json()
    assert all("Strategy Games" in g["categories"] for g in results)


def test_get_games_filter_by_players(client):
    response = client.get("/games/?players=2")
    assert response.status_code == 200
    results = response.json()
    assert all(
        g["min_players"] <= 2 <= g["max_players"]
        for g in results
    )

def test_get_games_players_out_of_range(client):
    response = client.get("/games/?players=0")
    assert response.status_code == 422


def test_get_games_limit_too_high(client):
    response = client.get("/games/?limit=999")
    assert response.status_code == 422


def test_get_game_by_id_success(client):
    response = client.get("/games/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data
    assert "mechanics" in data

def test_get_game_by_id_not_found(client):
    response = client.get("/games/99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_game_by_invalid_id(client):
    response = client.get("/games/notanid")
    assert response.status_code == 422


def test_get_trending_default(client):
    response = client.get("/games/trending")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)


def test_get_trending_ordered_by_rating(client):
    response = client.get("/games/trending?limit=2")
    results = response.json()
    if len(results) >= 2:
        assert results[0]["avg_rating"] >= results[1]["avg_rating"]

def test_get_trending_by_decade(client):
    response = client.get("/games/trending?decade=2015")
    assert response.status_code == 200
    results = response.json()
    assert all(
        2015 <= g["year_published"] < 2025
        for g in results
        if g["year_published"]
    )

def test_get_trending_limit(client):
    response = client.get("/games/trending?limit=1")
    assert response.status_code == 200
    assert len(response.json()) <= 1


def test_recommend_games_success(client):
    response = client.get("/games/recommend?mechanic=Hand Management")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert all("Hand Management" in g["mechanics"] for g in results)


def test_recommend_games_ordered_by_rating(client):
    response = client.get("/games/recommend?mechanic=Hand Management&limit=2")
    results = response.json()
    if len(results) >= 2:
        assert results[0]["avg_rating"] >= results[1]["avg_rating"]

def test_recommend_games_not_found(client):
    response = client.get("/games/recommend?mechanic=FakeMechanicXYZ")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_recommend_games_limit(client):
    response = client.get("/games/recommend?mechanic=Hand Management&limit=1")
    assert response.status_code == 200
    assert len(response.json()) <= 1