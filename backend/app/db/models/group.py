import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class GroupRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Group(BaseModel):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(500), default=None)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    memberships: Mapped[list["UserGroup"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", lazy="selectin"
    )
    creator: Mapped["User"] = relationship(lazy="selectin")


class UserGroup(BaseModel):
    __tablename__ = "user_groups"
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE")
    )
    role: Mapped[GroupRole] = mapped_column(
        Enum(GroupRole), default=GroupRole.MEMBER
    )

    user: Mapped["User"] = relationship(lazy="selectin")
    group: Mapped["Group"] = relationship(
        back_populates="memberships", viewonly=True
    )


from app.db.models.user import User  # noqa: E402
