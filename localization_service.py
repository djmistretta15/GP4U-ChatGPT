"""
Localization service.

Provides translation strings for supported languages.  This service
demonstrates how the backend can serve internationalised content to the
frontend.  In a real system the translations would be maintained in
separate files and loaded dynamically based on language codes.  Here
we embed a small dictionary for illustration purposes.
"""

from __future__ import annotations

from typing import Dict, List


class LocalizationService:
    """Service for retrieving translation strings."""

    # Hard‑coded translation data for demonstration purposes.
    _translations: Dict[str, Dict[str, str]] = {
        "en": {
            "welcome": "Welcome to the GPU Marketplace",
            "search": "Search for GPUs",
            "book": "Book a GPU",
            "price": "Price",
            "language": "Language",
        },
        "es": {
            "welcome": "Bienvenido al Mercado de GPU",
            "search": "Buscar GPUs",
            "book": "Reservar una GPU",
            "price": "Precio",
            "language": "Idioma",
        },
    }

    def list_languages(self) -> List[str]:
        """Return a list of supported language codes."""
        return list(self._translations.keys())

    def get_translations(self, lang: str) -> Dict[str, str]:
        """Return the translation dictionary for a given language code.

        If the language code is unknown, an empty dictionary is returned.
        """
        return self._translations.get(lang, {})