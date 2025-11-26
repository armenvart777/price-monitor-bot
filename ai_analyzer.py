from __future__ import annotations

import json
import logging
import anthropic

from config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> anthropic.Anthropic | None:
    global _client
    if not ANTHROPIC_API_KEY:
        return None
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def analyze_matches(
    price_list: list[dict],
    found_items: list[dict],
    marketplace: str,
) -> list[dict]:
    """Use Claude to match found marketplace items to price list.

    Returns list of matches with profit calculation.
    """
    ...
