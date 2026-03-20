def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data

def test_register_duplicate_username(client):
    client.post("/auth/register", json={
        "username": "dupeuser",
        "email": "dupe1@example.com",
        "password": "securepassword123"
    })
    response = client.post("/auth/register", json={
        "username": "dupeuser",
        "email": "dupe2@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "username": "emailuser1",
        "email": "shared@example.com",
        "password": "securepassword123"
    })
    response = client.post("/auth/register", json={
        "username": "emailuser2",
        "email": "shared@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_invalid_email(client):
    response = client.post("/auth/register", json={
        "username": "baduser",
        "email": "notanemail",
        "password": "securepassword123"
    })
    assert response.status_code == 422

def test_register_password_too_short(client):
    response = client.post("/auth/register", json={
        "username": "shortpass",
        "email": "shortpass@example.com",
        "password": "abc"
    })
    assert response.status_code == 422

def test_register_username_too_short(client):
    response = client.post("/auth/register", json={
        "username": "ab",
        "email": "shortname@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 422

def test_register_username_invalid_characters(client):
    response = client.post("/auth/register", json={
        "username": "bad user!",
        "email": "badchars@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 422

def test_login_success(client):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_unknown_user(client):
    response = client.post("/auth/login", data={
        "username": "ghostuser",
        "password": "doesntmatter"
    })
    assert response.status_code == 401

def test_get_me_success(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_me_invalid_token(client):
    response = client.get("/auth/me", headers={
        "Authorization": "Bearer totallynotavalidtoken"
    })
    assert response.status_code == 401