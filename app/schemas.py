from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
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
    personal_rating: Optional[float] = Field(default=None, ge=1.0, le=10.0)
    play_count: int = Field(default=0, ge=0)
    notes: Optional[str] = None

class CollectionUpdate(BaseModel):
    status: Optional[str] = None
    personal_rating: Optional[float] = Field(default=None, ge=1.0, le=10.0)
    play_count: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None

class CollectionResponse(CollectionCreate):
    id: int
    class Config:
        from_attributes = True