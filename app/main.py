from fastapi import FastAPI
from app.database import engine, Base
from app.routers import games, collection, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BGG Vault API",
    description="A board game collection tracker and analytics API powered by BoardGameGeek data.",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(collection.router, prefix="/collection", tags=["Collection"])

@app.get("/")
def root():
    return {"message": "Welcome to BGG Vault API"}