from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Collection, User
from app.schemas import CollectionResponse
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