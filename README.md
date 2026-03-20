# bgg-vault-api

A board game collection tracker and analytics API powered by BoardGameGeek data, built with FastAPI and SQLite.

## Overview
BGG Vault API lets users browse and discover board games from a dataset of ~20,000 titles sourced from BoardGameGeek, and manage a personal collection with play tracking and personalised recommendations. It provides analytics endpoints for trending games, mechanic-based discovery, and collection statistics.

Built with FastAPI, SQLAlchemy, and SQLite. Authentication is handled via JWT tokens.

## API Documentation

- **Swagger UI** (interactive, requires local server): http://127.0.0.1:8000/docs
- **Redoc** (interactive, requires local server): http://127.0.0.1:8000/redoc
- **PDF Reference**: [docs/api-documentation.pdf](https://github.com/deizlan/bgg-vault-api/blob/main/docs/api-documentation.pdf)

## Setup

1. Clone the repo and navigate into it
```bash
   git clone https://github.com/deezlan/bgg-vault-api.git
   cd bgg-vault-api
```

2. Create and activate a virtual environment
```bash
# Windows Command Prompt
python -m venv venv
venv\Scripts\activate.bat

# Windows PowerShell
python -m venv venv
venv\Scripts\Activate.ps1

# Windows Git Bash
python -m venv venv
source venv/Scripts/activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Configure environment variables
```bash
   cp .env.example .env
```
   Then open `.env` and set a secure `SECRET_KEY`.

5. Download the dataset from https://www.kaggle.com/datasets/andrewmvd/board-games  
   and place `bgg_dataset.csv` inside the `data/` folder.

6. Seed the database
```bash
   python seed.py
```

7. Run the API
```bash
   uvicorn app.main:app --reload
```

8. Open Swagger UI at http://127.0.0.1:8000/docs

## Authentication

The API uses JWT authentication via OAuth2 Password flow. To access protected endpoints in Swagger UI:

1. `POST /auth/register` — create an account
2. `POST /auth/login` — receive an access token
3. Click the **Authorize** button (🔓) at the top of Swagger UI
4. Enter your **username** and **password** and click **Authorize**

Swagger will handle attaching the token to all subsequent protected requests automatically.

Token lifetime is configured via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` (default: 30 minutes).

## Testing

The test suite uses pytest with an isolated SQLite test database. No seeding or setup is required — the test database is created and torn down automatically.

### Run all tests
```bash
pytest -v
```

### Run a specific test file
```bash
pytest tests/test_auth.py -v
pytest tests/test_games.py -v
pytest tests/test_collection.py -v
```

### Test coverage
| File | Tests |
|---|---|
| `tests/test_auth.py` | 13 |
| `tests/test_games.py` | 22 |
| `tests/test_collection.py` | 28 |
| **Total** | **63** |
