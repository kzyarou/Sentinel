from pydantic import BaseModel, Field
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
    external_id: str = Field(..., max_length=255)
    username: str = Field(..., max_length=100)
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    external_id: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=100)
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
