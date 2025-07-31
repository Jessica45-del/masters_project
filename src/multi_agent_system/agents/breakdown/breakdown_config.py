"""
Configuration for Breakdown Agent
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class BreakdownAgentConfig(BaseSettings):
   """ Configuration settings for Breakdown Agent"""
   # Orchestration model (plan & tool dispatch)
   model_name: str      = Field("deepseek-chat")
   temperature: float   = Field(0.2)
   api_key: str         = Field(default ="",alias="DEEPSEEK_API_KEY")


   # Jinja2 template for prompts
   template_dir: Path   = Field(Path(__file__).parents[2] / "prompts") # move up two levels in the dir structure
   template_file: str   = Field("diagnosis_prompt.jinja2")




   model_config = SettingsConfigDict(
       env_prefix="",
       populate_by_name=True,
   )

def get_config() -> BreakdownAgentConfig:
   cfg = BreakdownAgentConfig()
   return cfg

