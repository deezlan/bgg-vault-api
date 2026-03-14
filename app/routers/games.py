from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Game
from app.schemas import GameResponse, ErrorResponse

router = APIRouter()

@router.get("/", response_model=list[GameResponse], responses={
    422: {"model": ErrorResponse, "description": "Invalid query parameters"}
})
def get_games(
    search: Optional[str] = Query(None, description="Search by game title"),
    mechanic: Optional[str] = Query(None, description="Filter by mechanic e.g. 'Deck Construction'"),
    category: Optional[str] = Query(None, description="Filter by domain e.g. 'Strategy Games'"),
    players: Optional[int] = Query(default=None, ge=1, le=100, description="Filter by number of players supported"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """Browse and filter games with optional search and pagination."""
    query = db.query(Game)

    if search:
        query = query.filter(Game.title.ilike(f"%{search}%"))
    if mechanic:
        query = query.filter(Game.mechanics.ilike(f"%{mechanic}%"))
    if category:
        query = query.filter(Game.categories.ilike(f"%{category}%"))
    if players:
        query = query.filter(
            Game.min_players <= players,
            Game.max_players >= players
        )

    return query.offset(offset).limit(limit).all()

@router.get("/trending", response_model=list[GameResponse], responses={
    422: {"model": ErrorResponse, "description": "Invalid query parameters"}
})
def get_trending(
    decade: Optional[int] = Query(None, description="Filter by decade e.g. 2010 returns 2010-2019"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Return top rated games, optionally filtered by decade."""
    query = db.query(Game).filter(
        Game.avg_rating.isnot(None),
        Game.year_published.isnot(None)
    )

    if decade:
        query = query.filter(
            Game.year_published >= decade,
            Game.year_published < decade + 10
        )

    return query.order_by(Game.avg_rating.desc()).limit(limit).all()

@router.get("/recommend", response_model=list[GameResponse], responses={
    404: {"model": ErrorResponse, "description": "No games found for the requested mechanic"},
    422: {"model": ErrorResponse, "description": "Invalid query parameters"}
})
def recommend_games(
    mechanic: str = Query(..., description="Mechanic to base recommendations on e.g. 'Deck Construction'"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Recommend top rated games that feature a given mechanic."""
    games = db.query(Game).filter(
        Game.mechanics.ilike(f"%{mechanic}%"),
        Game.avg_rating.isnot(None)
    ).order_by(Game.avg_rating.desc()).limit(limit).all()

    if not games:
        raise HTTPException(
            status_code=404,
            detail=f"No games found featuring mechanic: '{mechanic}'"
        )

    return games

@router.get("/{game_id}", response_model=GameResponse, responses={
    404: {"model": ErrorResponse, "description": "Game not found"},
    422: {"model": ErrorResponse, "description": "game_id must be a valid integer"}
})
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get full details for a single game by ID."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game