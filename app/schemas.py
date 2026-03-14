from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must only contain letters, numbers or underscores")
        return v

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