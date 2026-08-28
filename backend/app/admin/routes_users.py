from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.db import repository
from app.db.models import User
from app.auth.dependencies import require_role
from app.schemas import UserResponse, UserUpdateRole, UserUpdateActive

router = APIRouter(prefix="/admin/users", tags=["Admin User Management"])


@router.get("", response_model=List[UserResponse])
def list_all_users(
    admin_user: User = Depends(require_role("admin"))
):
    """
    Admin-only: Retrieve all registered users with their roles and status.
    """
    return repository.list_users()


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    payload: UserUpdateRole,
    admin_user: User = Depends(require_role("admin"))
):
    """
    Admin-only: Promote or demote any user's role (admin, analyst, viewer).
    Prevents demoting an active admin if they are the only remaining active admin.
    """
    user = repository.get_user_by_id(str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    target_role = payload.role.lower()

    # Protect against system-wide admin lockout
    if user.role.lower() == "admin" and user.is_active and target_role != "admin":
        active_admins_count = repository.count_active_admins()
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the only remaining active admin account.",
            )

    repository.update_user(str(user_id), {"role": target_role})
    user.role = target_role
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def toggle_user_active_status(
    user_id: str,
    payload: UserUpdateActive,
    admin_user: User = Depends(require_role("admin"))
):
    """
    Admin-only: Deactivate or reactivate a user account.
    Prevents an admin from deactivating their own account or the last remaining active admin.
    """
    user = repository.get_user_by_id(str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Prevent self-deactivation
    if str(user.id) == str(admin_user.id) and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own admin account.",
        )

    # Prevent deactivating the last active admin
    if user.role.lower() == "admin" and user.is_active and not payload.is_active:
        active_admins_count = repository.count_active_admins()
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the only remaining active admin account.",
            )

    repository.update_user(str(user_id), {"is_active": payload.is_active})
    user.is_active = payload.is_active
    return user
