"""
AGENT 2: Grounding agent for diagnostic reasoning.
"""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.grounding.grounding_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import (
    find_mondo_id,
    extract_disease_label
)

config = get_config()

model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)

GROUNDING_SYSTEM_PROMPT = (
    "You are an expert in rare disease knowledge."
    "Your task is to provide additional ontological information about rare disease"
    "You will receive a disease label as input."
    "Your task is to find the MONDO ontology ID for this label using "
    "the find_mondo_id function."
)

# Create grounding agent
grounding_agent = Agent(
   model= model,
   system_prompt=GROUNDING_SYSTEM_PROMPT
)

# Register tools
grounding_agent.tool_plain(extract_disease_label)
grounding_agent.tool(find_mondo_id)


















