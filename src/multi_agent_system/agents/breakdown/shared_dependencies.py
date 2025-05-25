from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.breakdown.breakdown_config import BreakdownAgentConfig

config = BreakdownAgentConfig()

model = OpenAIModel(
    "deepseek-chat",
    provider=DeepSeekProvider(api_key=config.api_key),
)
