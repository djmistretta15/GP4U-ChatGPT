"""
Password reset token management service.

This service encapsulates the logic required to create and verify
password reset tokens.  A reset token is a one‑time code associated
with a user that expires after a configurable period.  When a token
is created, it is saved to the database and can be emailed to the
user.  When a token is presented along with a new password the
service verifies the token, updates the user's password and marks
the token as used.  Expired or used tokens are rejected.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import secrets
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.password_reset_token import PasswordResetToken
from backend.core.security import get_password_hash


class PasswordResetService:
    """Service for generating and redeeming password reset tokens."""

    def __init__(self, db: Session, token_lifetime_minutes: int = 60) -> None:
        self.db = db
        self.token_lifetime = timedelta(minutes=token_lifetime_minutes)

    def create_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for the user with the given email.

        Parameters
        ----------
        email: str
            The email address of the user requesting a password reset.

        Returns
        -------
        Optional[str]
            A token string if the user exists, otherwise ``None``.
        """
        user: Optional[User] = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        # Generate a cryptographically secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + self.token_lifetime
        token_obj = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            used=False,
        )
        self.db.add(token_obj)
        self.db.commit()
        self.db.refresh(token_obj)
        return token

    def verify_and_reset_password(self, token: str, new_password: str) -> bool:
        """Verify a password reset token and update the user's password.

        Parameters
        ----------
        token: str
            The password reset token presented by the user.
        new_password: str
            The new password to set for the user.

        Returns
        -------
        bool
            ``True`` if the password was reset successfully, ``False``
            if the token was invalid, expired or already used.
        """
        token_obj: Optional[PasswordResetToken] = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token == token)
            .first()
        )
        if not token_obj:
            return False
        # Reject if token has been used or is expired
        if token_obj.used or token_obj.expires_at < datetime.utcnow():
            return False
        # Look up the associated user
        user = self.db.query(User).get(token_obj.user_id)
        if not user:
            return False
        # Update the user's password
        user.hashed_password = get_password_hash(new_password)
        # Mark token as used
        token_obj.used = True
        self.db.commit()
        return True