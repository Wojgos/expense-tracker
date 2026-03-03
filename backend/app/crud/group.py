import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.group import Group, GroupRole, UserGroup


async def create_group(
    db: AsyncSession, name: str, description: str | None, creator_id: uuid.UUID
) -> Group:
    group = Group(name=name, description=description, created_by=creator_id)
    db.add(group)
    await db.flush()

    membership = UserGroup(
        user_id=creator_id, group_id=group.id, role=GroupRole.ADMIN
    )
    db.add(membership)
    await db.flush()
    return group


async def get_groups_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    stmt = (
        select(
            Group.id,
            Group.name,
            Group.description,
            Group.created_at,
            func.count(UserGroup.id).label("member_count"),
        )
        .join(UserGroup, UserGroup.group_id == Group.id)
        .where(
            Group.id.in_(
                select(UserGroup.group_id).where(UserGroup.user_id == user_id)
            )
        )
        .group_by(Group.id)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "created_at": r.created_at,
            "member_count": r.member_count,
        }
        for r in rows
    ]


async def get_group_by_id(db: AsyncSession, group_id: uuid.UUID) -> Group | None:
    return await db.get(Group, group_id)


async def update_group(
    db: AsyncSession, group: Group, name: str | None, description: str | None
) -> Group:
    if name is not None:
        group.name = name
    if description is not None:
        group.description = description
    await db.flush()
    return group


async def delete_group(db: AsyncSession, group: Group) -> None:
    await db.delete(group)
    await db.flush()


async def get_user_membership(
    db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID
) -> UserGroup | None:
    stmt = select(UserGroup).where(
        UserGroup.user_id == user_id, UserGroup.group_id == group_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_member(
    db: AsyncSession,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    role: GroupRole = GroupRole.MEMBER,
) -> UserGroup:
    membership = UserGroup(user_id=user_id, group_id=group_id, role=role)
    db.add(membership)
    await db.flush()
    return membership


async def remove_member(db: AsyncSession, membership: UserGroup) -> None:
    await db.delete(membership)
    await db.flush()
