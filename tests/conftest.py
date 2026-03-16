import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Game

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()

    # Seed test games
    games = [
        Game(
            bgg_id=1001,
            title="Test Game One",
            year_published=2020,
            min_players=2,
            max_players=4,
            play_time=60,
            complexity=2.5,
            avg_rating=8.0,
            mechanics="Deck Construction, Hand Management",
            categories="Strategy Games"
        ),
        Game(
            bgg_id=1002,
            title="Test Game Two",
            year_published=2015,
            min_players=1,
            max_players=2,
            play_time=30,
            complexity=1.5,
            avg_rating=7.5,
            mechanics="Dice Rolling, Hand Management",
            categories="Family Games"
        ),
    ]
    db.add_all(games)

    # Seed test user directly with hashed password
    from app.models import User
    from app.auth import hash_password
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    """Test client with database dependency overridden."""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def auth_headers(client):
    """Return auth headers with a valid JWT token."""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}