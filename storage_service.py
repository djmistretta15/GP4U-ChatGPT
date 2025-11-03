"""
Storage service.

This module provides a simple file and object storage abstraction. In
the context of GP4U it can be used to persist job checkpoints, user
uploads such as GPU images or verification documents, and any other
binary or JSON data that needs to be retrieved later. The default
implementation saves objects to the local filesystem, but the API is
designed so that it can be replaced with a cloud storage backend in
future iterations (e.g. AWS S3, Google Cloud Storage).
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict


class StorageService:
    """Local file‑based storage backend."""

    def __init__(self, base_path: str | None = None) -> None:
        # Use a directory relative to the project root if not provided
        self.base_path = base_path or os.path.join(os.getcwd(), "storage")
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, key: str, data: Dict[str, Any]) -> None:
        """Persist a JSON‑serialisable object under the given key."""
        filepath = os.path.join(self.base_path, f"{key}.json")
        with open(filepath, "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    async def load(self, key: str) -> Dict[str, Any]:
        """Load a JSON object previously saved under the given key."""
        filepath = os.path.join(self.base_path, f"{key}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No stored object found for key '{key}'")
        with open(filepath, encoding="utf-8") as handle:
            return json.load(handle)

    async def upload_file(self, filename: str, content: bytes) -> str:
        """Save a binary file and return a unique identifier for retrieval."""
        unique_key = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"
        file_path = os.path.join(self.base_path, unique_key)
        with open(file_path, "wb") as handle:
            handle.write(content)
        return unique_key

    def generate_file_url(self, key: str) -> str:
        """Generate a relative URL that can be used to retrieve the file."""
        return f"/media/{key}"

