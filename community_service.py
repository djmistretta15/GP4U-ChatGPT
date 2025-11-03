"""
Community service layer.

This service encapsulates the business logic for community features such as
following and unfollowing GPU owners.  It interacts with the ``Follow`` model
to persist relationships and provides convenience methods for listing
followed owners.  Future enhancements could include notifications when
followed owners add new GPUs or change pricing.
"""

from __future__ import annotations

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.follow import Follow


class CommunityService:
    """Service for managing follow relationships."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def follow_owner(self, follower_id: int, owner_id: int) -> Follow:
        """Create a follow relationship between two users.

        Parameters
        ----------
        follower_id: int
            The ID of the user who is following.
        owner_id: int
            The ID of the owner being followed.

        Returns
        -------
        Follow
            The created follow relationship.
        """
        if follower_id == owner_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
        # Check for existing follow
        existing = (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.owner_id == owner_id)
            .first()
        )
        if existing:
            return existing
        follow = Follow(follower_id=follower_id, owner_id=owner_id)
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)
        return follow

    def unfollow_owner(self, follower_id: int, owner_id: int) -> None:
        """Remove a follow relationship if it exists."""
        follow = (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.owner_id == owner_id)
            .first()
        )
        if not follow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow relationship not found")
        self.db.delete(follow)
        self.db.commit()

    def list_following(self, follower_id: int) -> List[int]:
        """Return a list of owner IDs that the given user is following."""
        follows = (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id)
            .all()
        )
        return [f.owner_id for f in follows]