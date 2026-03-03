import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.models.group import GroupRole


class GroupCreate(BaseModel):
    name: str
    description: str | None = None


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class MemberResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    email: str
    role: GroupRole

    model_config = {"from_attributes": True}


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_by: uuid.UUID
    created_at: datetime
    members: list[MemberResponse] = []

    model_config = {"from_attributes": True}


class GroupListItem(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    member_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
