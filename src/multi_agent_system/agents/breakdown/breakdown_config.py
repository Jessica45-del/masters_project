from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class BreakdownAgentConfig(BaseSettings):
    """Holds all config settings for the Phenopacket Agent."""
    # Orchestration model (plan & tool dispatch)
    model_name: str      = Field("deepseek-r1")
    max_tokens: int      = Field(256)
    temperature: float   = Field(0.3)
    api_key: str         = Field(alias="DEEPSEEK_API_KEY")

    # Jinja2 template for prompts
    template_dir: Path   = Field(Path("src/multi_agent_system/prompts"))
    template_file: str   = Field("diagnosis_prompt.jinja2")

    # Output directory for initial diagnoses
    output_dir: Path = Path("initial_diagnosis")

    # Pydantic v2 settings: no .env file, use direct env var names if set
    model_config = SettingsConfigDict(
        env_prefix="",
        populate_by_name=True,
    )

def get_config():
    return BreakdownAgentConfig()