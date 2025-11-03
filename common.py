"""
Common response schemas.

Provides simple message and error response models for API endpoints.
"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str

