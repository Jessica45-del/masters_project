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
    "You are an expert in rare disease ontologies."
    "Your task is to enrich diagnostic output with MONDO identifiers."
    "You will work with results from an breakdown agent which include "
    "disease candidate labels. "
    "Follow this workflow for each patient file: "
    "1.For each patient results file (a `.json` file located in the initial diagnosis directory)"
    "use the 'extract_disease_label to extract patient disease labels"
    "2.Then use the disease labels to find the MONDO ontology ID for the label using "
    "the find_mondo_id function."
    "3. Return the results as a JSON list of objects. "
    "Each object must contain the disease `label` and its corresponding MONDO `id`."
    "If no MONDO match is found, return null for the ID."
    "Use only the provided functions to complete this task."
)

# Create grounding agent
grounding_agent = Agent(
   model= model,
   system_prompt=GROUNDING_SYSTEM_PROMPT
)

# Register tools
grounding_agent.tool_plain(extract_disease_label)
grounding_agent.tool_plain(find_mondo_id)


















