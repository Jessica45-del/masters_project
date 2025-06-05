"""
Configuration for Grounding Agent.
"""
from dataclasses import dataclass
from typing import Optional
from pydantic import Field
from pathlib import Path
from oaklib.implementations import MonarchImplementation
from pydantic_settings import BaseSettings, SettingsConfigDict


# Constants
HAS_PHENOTYPE = "biolink:has_phenotype"  # Is this necessary. I read that

@dataclass
class GroundingAgentConfig(BaseSettings):
    """ Configuration for Grounding Agent. """

    # The maximum number of search results to be returned
    max_search_results: int = 10

    # Monarch Adapter
    monarch_adapter: Optional[MonarchImplementation] = None

    # Control randomness of model output. Lower = less randomness.
    temperature: float = Field(0.0)

    api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")