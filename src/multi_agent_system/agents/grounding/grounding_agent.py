"""
AGENT 2:
Grounding agent for retrieval of external data that is part of the multi-system
diagnostic reasoning agent
"""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

GROUNDING_SYSTEM_PROMPT(
    "You are an expert in rare disease knowledge."
    "Your task is to retrieve information about the disease from:"
    "1) The Monarch KB"
    "2) and Map MONDO ID to HPO terms."
    "The recommended workflow is to first...."
    "Use the Monarch Knowledge Graph to find relevant disease information."
    "For each disease candidate, collect all associated phenotypes."
    "Provide a detailed analysis of each disease candidate, including ID, label, and phenotypes."
    "You will a."
)




grounding_agent = Agent(
    model ="g",
    deps_type = GroundingDependencies,
    result_type=str, # or JSON?
    system_prompt=GROUNDING_SYSTEM_PROMPT
)


