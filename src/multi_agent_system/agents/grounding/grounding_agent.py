"""
AGENT 2: Grounding agent for diagnostic reasoning.
"""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.grounding.grounding_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import (
    find_mondo_id,
    extract_disease_label,
    find_disease_knowledge,
)

config = get_config()

model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)

GROUNDING_SYSTEM_PROMPT = (
    "You are an expert in rare disease ontologies.  "
    "Your task is to enrich diagnostic results by:"
    "1. Extracting candidate disease labels from JSON patient diagnosis files using "
    "the extract_disease_label function."
    "2. For each disease label, use the find_mondo_id function to map it to a MONDO identifier."
    "3. For each MONDO ID you find, use the get_disease_knowledge function to "
    "retrieve phenotypic associations (e.g., HPO terms)."
    "4. Return a list of objects. Each object must include:"
    "- the original disease `label`"
    "- the MONDO `id`"
    "- and a list of associated phenotypes from the Monarch knowledge base "
    "under a `phenotypes` key."
    "If no MONDO match is found, include `id': null` and an empty list for 'phenotypes'"
    "Use only the registered functions to complete this task."
)

# Create grounding agent
grounding_agent = Agent(
   model= model,
   system_prompt=GROUNDING_SYSTEM_PROMPT
)

# Register tools
grounding_agent.tool_plain(extract_disease_label)
grounding_agent.tool_plain(find_mondo_id)
grounding_agent.tool_plain(find_disease_knowledge)


















