"""
Authentication schemas.

Defines request and response models for login and token handling.
"""

from pydantic import BaseModel, EmailStr, constr


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: constr(min_length=8)


class TokenResponse(BaseModel):
    """Response model for access tokens."""
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: constr(min_length=8)


class ForgotPasswordRequest(BaseModel):
    """Request body to initiate a password reset."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body to complete a password reset."""
    token: str
    password: constr(min_length=8)

