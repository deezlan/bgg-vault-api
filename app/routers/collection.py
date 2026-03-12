from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Collection, Game, User
from app.schemas import CollectionCreate, CollectionResponse
from app.auth import get_current_user

router = APIRouter()

VALID_STATUSES = {"owned", "wishlist", "played"}

@router.get("/", response_model=list[CollectionResponse])
def get_collection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's full collection."""
    return db.query(Collection).filter(
        Collection.user_id == current_user.id
    ).all()

@router.post("/", response_model=CollectionResponse, status_code=201)
def add_to_collection(
    entry: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a game to the current user's collection."""
    if entry.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    game = db.query(Game).filter(Game.id == entry.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    existing = db.query(Collection).filter(
        Collection.user_id == current_user.id,
        Collection.game_id == entry.game_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Game already in collection")

    item = Collection(
        user_id=current_user.id,
        game_id=entry.game_id,
        status=entry.status,
        personal_rating=entry.personal_rating,
        play_count=entry.play_count,
        notes=entry.notes
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
