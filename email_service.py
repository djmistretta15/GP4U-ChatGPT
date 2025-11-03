"""
Email service implementation for sending transactional emails.

This module provides a simple wrapper around the SendGrid API to send
verification and password reset emails. If a SendGrid API key is not
configured, the methods will gracefully fall back to logging the email
contents to stdout instead of raising exceptions. This makes it easier
to develop and test the application without relying on third‑party
services.

The API key can be provided either explicitly via the constructor or
through the ``SENDGRID_API_KEY`` environment variable. Similarly, the
``DEFAULT_FROM_EMAIL`` environment variable can be used to specify the
default sender address.
"""

from __future__ import annotations

import os
from typing import Optional

try:
    from sendgrid import SendGridAPIClient  # type: ignore
    from sendgrid.helpers.mail import Mail  # type: ignore
except ImportError:
    # The SendGrid library is optional. If it is not installed, the
    # EmailService will still work in a degraded mode by printing
    # messages to the console instead of sending real emails.
    SendGridAPIClient = None
    Mail = None


class EmailService:
    """Service for sending transactional emails via SendGrid."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@gp4u.com")
        if self.api_key and SendGridAPIClient:
            self.client: Optional[SendGridAPIClient] = SendGridAPIClient(self.api_key)
        else:
            # If no API key is provided or the library is missing, set client to None.
            self.client = None

    def _send(self, to_email: str, subject: str, content: str) -> None:
        """Internal helper to send or log an email."""
        if not self.client:
            # Fallback behaviour: log the email for debugging.
            print(
                f"EmailService (mock): To={to_email}, Subject={subject}, Content={content}"
            )
            return
        # Compose and send the email via SendGrid.
        assert Mail is not None  # for type checking
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content,
        )
        try:
            self.client.send(message)
        except Exception as exc:  # pragma: no cover - SendGrid errors are logged
            print(f"EmailService: error sending email: {exc}")

    def send_verification_email(self, to_email: str, token: str) -> None:
        """Send an account verification email to the specified address."""
        verification_link = f"https://gp4u.com/verify?token={token}"
        subject = "Verify your GP4U account"
        body = (
            "Thank you for registering with GP4U! "
            "To complete your sign up, please verify your email by visiting the following link:\n\n"
            f"{verification_link}\n\n"
            "If you did not create an account, please ignore this message."
        )
        self._send(to_email, subject, body)

    def send_password_reset_email(self, to_email: str, token: str) -> None:
        """Send a password reset email to the specified address."""
        reset_link = f"https://gp4u.com/reset-password?token={token}"
        subject = "Reset your GP4U password"
        body = (
            "We received a request to reset your GP4U password. "
            "You can reset your password by clicking the link below:\n\n"
            f"{reset_link}\n\n"
            "If you did not request a password reset, please ignore this email."
        )
        self._send(to_email, subject, body)

