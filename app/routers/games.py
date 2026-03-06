from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Game
from app.schemas import GameResponse

router = APIRouter()

@router.get("/", response_model=list[GameResponse])
def get_games(
    search: Optional[str] = Query(None, description="Search by game title"),
    mechanic: Optional[str] = Query(None, description="Filter by mechanic e.g. 'Deck Construction'"),
    category: Optional[str] = Query(None, description="Filter by domain e.g. 'Strategy Games'"),
    players: Optional[int] = Query(None, description="Filter by number of players supported"),
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