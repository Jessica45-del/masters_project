"""
 Configuration for the Grounding Agent.
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from oaklib.implementations import MonarchImplementation


@dataclass
class GroundingAgentConfig:
    """Configuration for the Grounding Agent."""

    # Max number of search results to return
    max_search_results: int = 10

    # Monarch adapter for retrieving disease knowledge
    monarch_adapter: Optional[MonarchImplementation] = None

    #api key
    api_key: str = field(default_factory=lambda: os.environ.get("DEEPSEEK_API_KEY", ""))

    def __post_init__(self):
        """Initialize the Monarch adapter if not provided."""
        if self.monarch_adapter is None:
            self.monarch_adapter = MonarchImplementation()


def get_config() -> GroundingAgentConfig:
    return GroundingAgentConfig()














































# from pathlib import Path
# from typing import Optional
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field
# from oaklib import get_adapter
# from oaklib.interfaces import SearchInterface
#
#
# class GroundingAgentConfig(BaseSettings):
#     """Configuration for the Grounding Agent."""
#
#     # Max number of MONDO search results to return
#     max_search_results: int = Field(10)
#
#     # Adapter for MONDO lookup (sqlite-based)
#     mondo_adapter: Optional[SearchInterface] = None
#
#     api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
#
#     model_config = SettingsConfigDict(
#         env_prefix="",
#         populate_by_name=True,
#     )
#
#
# def get_config() -> GroundingAgentConfig:
#     """Load config and initialize the MONDO adapter if not provided."""
#     cfg = GroundingAgentConfig()
#
#     if cfg.mondo_adapter is None:
#         cfg.mondo_adapter = get_adapter("sqlite:obo:mondo")
#
#     return cfg

