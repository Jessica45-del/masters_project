"""
Configuration for the Grounding Agent using the SQLite MONDO adapter.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from oaklib import get_adapter
from oaklib.interfaces import SearchInterface


class GroundingAgentConfig(BaseSettings):
    """Configuration for the Grounding Agent."""

    # Max number of MONDO search results to return
    max_search_results: int = Field(10)

    # Adapter for MONDO lookup (sqlite-based)
    mondo_adapter: Optional[SearchInterface] = None

    # API key (optional — if you later call a model)
    api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")

    model_config = SettingsConfigDict(
        env_prefix="",
        populate_by_name=True,
    )


def get_config() -> GroundingAgentConfig:
    """Load config and initialize the MONDO adapter if not provided."""
    cfg = GroundingAgentConfig()

    if cfg.mondo_adapter is None:
        cfg.mondo_adapter = get_adapter("sqlite:obo:mondo")

    return cfg
