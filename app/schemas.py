from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class GameBase(BaseModel):
    title: str
    year_published: Optional[int]
    min_players: Optional[int]
    max_players: Optional[int]
    play_time: Optional[int]
    complexity: Optional[float]
    avg_rating: Optional[float]
    mechanics: Optional[str]
    categories: Optional[str]

class GameResponse(GameBase):
    id: int
    bgg_id: int
    class Config:
        from_attributes = True

class CollectionCreate(BaseModel):
    game_id: int
    status: str
    personal_rating: Optional[float] = None
    play_count: int = 0
    notes: Optional[str] = None

class CollectionUpdate(BaseModel):
    status: Optional[str] = None
    personal_rating: Optional[float] = None
    play_count: Optional[int] = None
    notes: Optional[str] = None

class CollectionResponse(CollectionCreate):
    id: int
    class Config:
        from_attributes = True