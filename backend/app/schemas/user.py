from pydantic import BaseModel, Field
from pydantic import EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class UserBase(BaseModel):
    external_id: Optional[str] = Field(None, max_length=255)
    username: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    external_id: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserInDBBase(UserBase):
    id: str
    created_timestamp: datetime
    updated_timestamp: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserLogin(BaseModel):
    username: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str  # User ID
    exp: int  # Expiration timestamp
    role: str  # User role
