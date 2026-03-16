# bgg-vault-api

A board game collection tracker and analytics API powered by BoardGameGeek data, built with FastAPI and SQLite.

## Setup

1. Clone the repo and navigate into it
```bash
   git clone https://github.com/yourusername/bgg-vault-api.git
   cd bgg-vault-api
```

2. Create and activate a virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
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

## Data

The dataset used is the Board Games dataset from BoardGameGeek, 
sourced from Kaggle (andrewmvd/board-games).

**To seed the database:**
1. Download `bgg_dataset.csv` from https://www.kaggle.com/datasets/andrewmvd/board-games
2. Place it in this `data/` folder
3. Run `python seed.py`

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

## API Documentation

Interactive documentation is available via Swagger UI when the API is running locally:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **Redoc**: http://127.0.0.1:8000/redoc
- **PDF**: See `docs/api-documentation.pdf`