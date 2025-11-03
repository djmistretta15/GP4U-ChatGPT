"""
OAuth integration service.

This module defines a minimal service for handling OAuth login flows
for third‑party providers such as Google or GitHub. In a production
system you would integrate with libraries like `authlib` or
`python-social-auth` to generate authorization URLs, exchange
authorization codes for access tokens and fetch user information.

For the purposes of this demonstration, the service provides simple
stub methods that return predictable values. These methods can be
expanded in the future to integrate with real OAuth providers.
"""

from __future__ import annotations

from typing import Optional, Dict

from sqlalchemy.orm import Session

import secrets


class OAuthService:
    """Simple OAuth login service with basic user provisioning.

    This service demonstrates how an OAuth flow might be handled in the
    backend.  It constructs an authorization URL for a given provider
    and, upon receiving a callback with an authorization code, either
    looks up an existing user or creates a new one.  In a production
    system you would use an OAuth client library such as ``authlib`` to
    perform the code exchange and fetch user profile information.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_login_url(self, provider: str) -> str:
        """Generate an authorization URL for the specified provider.

        The returned URL includes a placeholder client ID and a fixed
        redirect URI.  In practice you would configure client IDs and
        redirect URIs via environment variables or settings.  You may
        also include state parameters for CSRF protection.  Scopes are
        omitted for simplicity.
        """
        base_url = f"https://{provider}.example.com/oauth/authorize"
        client_id = "dummy-client-id"
        redirect_uri = "https://gp4u.com/oauth/callback"
        return f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

    async def handle_callback(self, provider: str, code: str) -> Optional[Dict[str, str]]:
        """Handle the OAuth callback and return user information.

        In lieu of exchanging the code for an access token, we treat
        the ``code`` parameter as a unique identifier from the provider.
        We derive a synthetic email address from the provider and code
        (e.g. ``{code}@{provider}.oauth``) and ensure a corresponding
        user exists in the database.  The method returns a dictionary
        containing the newly created or existing user's ID and email.

        Parameters
        ----------
        provider: str
            The name of the OAuth provider (e.g. ``google`` or ``github``).
        code: str
            The authorization code returned by the provider after the
            user authorises the application.

        Returns
        -------
        Optional[Dict[str, str]]
            A dictionary with user information, or ``None`` if the
            provider or code is invalid.
        """
        if not provider or not code:
            return None
        # Build a synthetic email.  This ensures idempotent user
        # creation: if the provider returns the same code for the same
        # user, we will look up the user by email and avoid creating
        # duplicates.  In a real OAuth implementation you would fetch
        # the user's email from the provider's API.
        synthetic_email = f"{code}@{provider}.oauth"
        from backend.models.user import User  # imported here to avoid circular import
        from backend.core.security import get_password_hash
        # Attempt to find an existing user with this email
        user = self.db.query(User).filter(User.email == synthetic_email).first()
        if not user:
            # Create a new user with a random password; the password
            # should never be used since authentication is via OAuth,
            # but we still need to satisfy the ``hashed_password`` field.
            user = User(
                email=synthetic_email,
                hashed_password=get_password_hash(secrets.token_urlsafe(16)),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return {"user_id": user.id, "email": user.email}

