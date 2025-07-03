"""
AGENT 2: Grounding agent for diagnostic reasoning.
"""
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.grounding.grounding_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import (
    find_mondo_id,
    find_disease_knowledge,
    GroundedDiseaseResult,
)

config = get_config()

model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)

GROUNDING_SYSTEM_PROMPT = (
    """
    You are an expert in rare disease ontologies.  
    Your task is to enrich diagnostic results by:
    You will be given a list of candidate disease names as input.
    For each disease name in the list:
    1. Use the 'find_mondo_id' function to map it to a MONDO ID.
    2. Use the 'get_disease_knowledge' function for that MONDO ID to retrieve phenotypic associations (e.g HPO terms).
    
    Output:
    - You must return the original disease 'disease_name'
    - You must return the MONDO ID 'mondo_id'
    - You must return a list of associated phenotypes (For each disease, only return the first 10 associated HPO IDs)
    
    If no MONDO match is found, include `MONDO ID': null` and an empty list for 'phenotypes'
    You must return the result as valid JSON, and the entire response must fit within the token limit.
    Do not include explanations, markdown formatting, or natural language. 
    """
)

# Create grounding agent
grounding_agent = Agent(
    model= model,
    system_prompt=GROUNDING_SYSTEM_PROMPT,
    output_type= GroundedDiseaseResult

)

# Register tools
grounding_agent.tool_plain(find_mondo_id)
grounding_agent.tool_plain(find_disease_knowledge)


















