from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
from app.database import get_db
from app.models import Collection, Game, User
from app.schemas import CollectionCreate, CollectionUpdate, CollectionResponse, GameResponse
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

@router.patch("/{item_id}", response_model=CollectionResponse)
def update_collection_item(
    item_id: int,
    updates: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a collection entry's status, rating, play count or notes."""
    item = db.query(Collection).filter(
        Collection.id == item_id,
        Collection.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Collection item not found")

    if updates.status and updates.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def remove_from_collection(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a game from the current user's collection."""
    item = db.query(Collection).filter(
        Collection.id == item_id,
        Collection.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Collection item not found")

    db.delete(item)
    db.commit()

@router.get("/stats")
def get_collection_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return analytics summary for the current user's collection."""
    items = db.query(Collection).filter(
        Collection.user_id == current_user.id
    ).all()

    if not items:
        return {"message": "Your collection is empty."}

    game_ids = [item.game_id for item in items]
    games = db.query(Game).filter(Game.id.in_(game_ids)).all()
    game_map = {game.id: game for game in games}

    # Complexity average
    complexities = [
        game_map[item.game_id].complexity
        for item in items
        if game_map.get(item.game_id) and game_map[item.game_id].complexity
    ]
    avg_complexity = round(sum(complexities) / len(complexities), 2) if complexities else None

    # Personal rating average
    ratings = [item.personal_rating for item in items if item.personal_rating]
    avg_personal_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    # Status breakdown
    status_counts = Counter(item.status for item in items)

    # Favourite mechanics — flatten all mechanics, count occurrences
    all_mechanics = []
    for item in items:
        game = game_map.get(item.game_id)
        if game and game.mechanics:
            all_mechanics.extend(
                [m.strip() for m in game.mechanics.split(",")]
            )
    top_mechanics = [m for m, _ in Counter(all_mechanics).most_common(5)]

    # Total play count
    total_plays = sum(item.play_count for item in items)

    return {
        "total_games": len(items),
        "status_breakdown": dict(status_counts),
        "average_complexity": avg_complexity,
        "average_personal_rating": avg_personal_rating,
        "top_mechanics": top_mechanics,
        "total_plays": total_plays
    }

@router.get("/recommend", response_model=list[GameResponse])
def recommend_from_collection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest games not in the user's collection based on their top mechanics."""
    items = db.query(Collection).filter(
        Collection.user_id == current_user.id
    ).all()

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Your collection is empty. Add some games first."
        )

    game_ids = [item.game_id for item in items]
    games = db.query(Game).filter(Game.id.in_(game_ids)).all()

    # Find top 3 mechanics from collection
    all_mechanics = []
    for game in games:
        if game.mechanics:
            all_mechanics.extend([m.strip() for m in game.mechanics.split(",")])

    if not all_mechanics:
        raise HTTPException(
            status_code=400,
            detail="No mechanics data found in your collection."
        )

    top_mechanics = [m for m, _ in Counter(all_mechanics).most_common(3)]

    # Find highly rated games with those mechanics not already in collection
    recommendations = []
    seen_ids = set(game_ids)

    for mechanic in top_mechanics:
        matches = db.query(Game).filter(
            Game.mechanics.ilike(f"%{mechanic}%"),
            Game.avg_rating.isnot(None),
            ~Game.id.in_(seen_ids)
        ).order_by(Game.avg_rating.desc()).limit(5).all()

        for match in matches:
            if match.id not in seen_ids:
                recommendations.append(match)
                seen_ids.add(match.id)

    return recommendations[:10]