import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.group import (
    add_member,
    create_group,
    delete_group,
    get_group_by_id,
    get_groups_for_user,
    get_user_membership,
    remove_member,
    update_group,
)
from app.crud.user import get_user_by_id
from app.db.models.group import GroupRole
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.group import (
    GroupCreate,
    GroupListItem,
    GroupResponse,
    GroupUpdate,
    MemberResponse,
)

router = APIRouter(prefix="/groups", tags=["groups"])


def _build_group_response(group) -> GroupResponse:
    members = [
        MemberResponse(
            user_id=m.user.id,
            display_name=m.user.display_name,
            email=m.user.email,
            role=m.role,
        )
        for m in group.memberships
    ]
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        created_at=group.created_at,
        members=members,
    )


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group_endpoint(
    data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await create_group(db, data.name, data.description, current_user.id)
    await db.refresh(group)
    return _build_group_response(group)


@router.get("/", response_model=list[GroupListItem])
async def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_groups_for_user(db, current_user.id)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    return _build_group_response(group)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group_endpoint(
    group_id: uuid.UUID,
    data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership or membership.role != GroupRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update the group")

    group = await get_group_by_id(db, group_id)
    group = await update_group(db, group, data.name, data.description)
    await db.refresh(group)
    return _build_group_response(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_endpoint(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership or membership.role != GroupRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete the group")

    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    await delete_group(db, group)


# ---------- Member management ----------


@router.post("/{group_id}/members/{user_id}", response_model=MemberResponse)
async def add_member_endpoint(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_user_membership(db, current_user.id, group_id)
    if not membership or membership.role != GroupRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can add members")

    target_user = await get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await get_user_membership(db, user_id, group_id)
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member")

    new_membership = await add_member(db, group_id, user_id)
    return MemberResponse(
        user_id=target_user.id,
        display_name=target_user.display_name,
        email=target_user.email,
        role=new_membership.role,
    )


@router.delete(
    "/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member_endpoint(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    caller_membership = await get_user_membership(db, current_user.id, group_id)
    if not caller_membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    is_self_leave = current_user.id == user_id
    is_admin = caller_membership.role == GroupRole.ADMIN

    if not is_self_leave and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can remove other members")

    target_membership = await get_user_membership(db, user_id, group_id)
    if not target_membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    if target_membership.role == GroupRole.ADMIN and not is_self_leave:
        raise HTTPException(status_code=403, detail="Cannot remove another admin")

    await remove_member(db, target_membership)
