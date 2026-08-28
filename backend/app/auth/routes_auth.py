import datetime
from datetime import timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from app.db import repository
from app.db.models import User, PasswordReset
from app.auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_reset_token,
    hash_reset_token
)
from app.auth.dependencies import get_current_user
from app.auth.email_service import send_password_reset_email
from app.auth.google_oauth import oauth, verify_google_token_or_code
from app.config import settings
from app.schemas import (
    UserRegister,
    UserLogin,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    MessageResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister):
    """
    Registers a new user.
    If this is the first user in the database, automatically grants 'admin' role;
    otherwise assigns 'viewer' by default.
    """
    existing_user = repository.get_user_by_email(payload.email.lower().strip())
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Determine default role (first user becomes admin, subsequent users become viewer)
    total_users = repository.count_users()
    initial_role = "admin" if total_users == 0 else "viewer"

    hashed_pw = get_password_hash(payload.password)
    new_user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed_pw,
        auth_provider="local",
        role=initial_role,
        is_active=True,
    )
    new_user = repository.create_user(new_user)

    token = create_access_token({
        "sub": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role,
        "name": new_user.name
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user, from_attributes=True)
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin):
    """
    Authenticates a user with email and password, returning a JWT token with embedded role claims.
    """
    user = repository.get_user_by_email(payload.email.lower().strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact an administrator.",
        )

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.name
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user, from_attributes=True)
    )


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest):
    """
    Generates a secure password reset token and emails it to the user.
    Always returns a generic message to prevent email enumeration.
    """
    user = repository.get_user_by_email(payload.email.lower().strip())
    if user and user.is_active:
        raw_token = generate_reset_token()
        token_hash = hash_reset_token(raw_token)
        expires_at = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)

        # Save reset record (expires in 30 mins)
        reset_entry = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False
        )
        repository.create_password_reset(reset_entry)

        # Send email with raw token
        send_password_reset_email(user.email, raw_token)

    return MessageResponse(
        message="If that email is registered in our system, a password reset link has been dispatched."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest):
    """
    Verifies the reset token, updates the user's password, and marks the token used.
    """
    token_hash = hash_reset_token(payload.token.strip())
    now_utc = datetime.datetime.now(timezone.utc)

    reset_entry = repository.get_password_reset_by_token_hash(token_hash)

    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid, already used, or expired.",
        )

    # Check expiry in application code (validated in application code for safety)
    if reset_entry.expires_at.replace(tzinfo=timezone.utc) < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid, already used, or expired.",
        )

    user = repository.get_user_by_id(reset_entry.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account was not found.",
        )

    # Update password and mark token used
    repository.update_user(user.id, {"password_hash": get_password_hash(payload.new_password)})
    repository.mark_password_reset_used(reset_entry.id)

    return MessageResponse(
        message="Password has been successfully updated. You may now log in with your new password."
    )


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiates Google OAuth2 consent flow.
    """
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        return await oauth.google.authorize_redirect(request, redirect_uri)
    else:
        # Development placeholder redirection
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?oauth_demo=google")


@router.get("/google/callback")
async def google_callback(code: Optional[str] = None):
    """
    Handles Google OAuth2 callback, verifies user, creates account if new, and redirects to frontend with JWT.
    """
    if not code:
        # Demo fallback
        profile = await verify_google_token_or_code("", settings.GOOGLE_REDIRECT_URI)
    else:
        profile = await verify_google_token_or_code(code, settings.GOOGLE_REDIRECT_URI)

    if not profile or "email" not in profile:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=google_auth_failed")

    email = profile["email"].lower().strip()
    name = profile.get("name", "Google User")
    google_id = profile.get("sub")

    user = repository.get_user_by_email(email)
    if not user:
        total_users = repository.count_users()
        initial_role = "admin" if total_users == 0 else "viewer"
        user = User(
            name=name,
            email=email,
            password_hash=None,
            auth_provider="google",
            google_id=google_id,
            role=initial_role,
            is_active=True,
        )
        user = repository.create_user(user)
    else:
        if not user.google_id and google_id:
            repository.update_user(user.id, {"google_id": google_id})
            user.google_id = google_id

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.name
    })

    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={token}")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user's profile and active role.
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
def logout_user(current_user: User = Depends(get_current_user)):
    """
    Acknowledges user logout. Client-side clears JWT token from storage.
    """
    return MessageResponse(message="Successfully logged out.")
