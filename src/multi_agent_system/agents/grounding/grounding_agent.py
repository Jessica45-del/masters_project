"""
AGENT 2:
Grounding agent for retrieval of external data that is part of the multi-system
diagnostic reasoning agent
"""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.openai import OpenAIProvider

from multi_agent_system.agents.grounding.grounding_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import find_mondo_id

config = get_config()

model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider()
)

GROUNDING_SYSTEM_PROMPT = (
    "You are an expert in rare disease knowledge."
    "Your task is to provide additional ontological information about rare disease"
    "You will perform this task by completing the following steps:"
    "1) Extract candidate disease labels from initial_diagnosis result files"
    "2) Map HPO ID (terms) to MONDO disease IDs using the find_mondo_id function"
    "3 Return results as a JSON list."
    ""
)


# Create grounding agent
grounding_agent = Agent(
   model= model,
   system_prompt=GROUNDING_SYSTEM_PROMPT
)

# Register tools
grounding_agent.tool(find_mondo_id)


















