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
   max_tokens: int      = Field(256)
   temperature: float   = Field(0.0)
   api_key: str         = Field(default ="",alias="DEEPSEEK_API_KEY")


   # Jinja2 template for prompts
   template_dir: Path   = Field(Path(__file__).parents[2] / "prompts") # move up two levels in the dir structure
   template_file: str   = Field("diagnosis_prompt.jinja2")


   # Results directory and subdirectory
   results_dir: Path = Field(Path("results"))
   initial_diagnosis_subdir: str = Field("initial_diagnosis")

# avoids hardcoding output directory
   @property
   def output_dir(self) -> Path:
       return self.results_dir / self.initial_diagnosis_subdir

   model_config = SettingsConfigDict(
       env_prefix="",
       populate_by_name=True,
   )

def get_config() -> BreakdownAgentConfig:
   cfg = BreakdownAgentConfig()
   cfg.output_dir.mkdir(parents=True, exist_ok=True)  # Create results/initial_diagnosis
   return cfg

