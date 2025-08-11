"""
Configuration for Similarity Agent
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class SimilarityAgentConfig(BaseSettings):
    """Configuration settings for the similarity scoring agent."""

    # Jaccard similarity threshold for considering a strong match
    similarity_threshold: float = Field(0.3, description="Minimum Jaccard score to consider a match")

    # Limit on number of top diseases to return
    top_n_results: int = Field(5, description="Maximum number of top-scoring disease matches to return")

    # API key
    api_key: str = Field(default="", alias="DEEPSEEK_API_KEY") #deepseek
    #api_key: str = Field(default="", alias="OPEN_API_KEY") #open ai

    model_config = SettingsConfigDict(
        env_prefix="",
        populate_by_name=True,
    )


def get_config() -> SimilarityAgentConfig:
    """Returns the configured settings for the similarity agent."""
    return SimilarityAgentConfig()
