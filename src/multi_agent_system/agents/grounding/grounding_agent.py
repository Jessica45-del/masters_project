"""
AGENT 2: Grounding agent for diagnostic reasoning.
"""
from typing import List

#from oaklib.cli import settings
from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

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
    Your task is to enrich diagnostic results.
    You will be given a list of candidate disease names as input.
    For each disease name in the list:
    1. You must map the candidate disease to its MONDO ID using the 'find_mondo_id' function.
    2. You must use the MONDO ID  to retrieve a list of associated phenotypes (objects with 'hpo_id') using 
    the 'get_disease_knowledge function
    You must complete these two tasks before moving on to another task.
    
    Output:
    - You must return the original disease 'disease_name'
    - You must return the MONDO ID 'mondo_id'
    - You must return a list of associated phenotypes (for each disease, you be return only associated HPO ID, 
    you must not return MONDO IDs)
    
    IMPORTANT NOTES:
    You must call 'find_mondo_id' and 'retrieve_disease_knowledge for every disease. Do not skip any. 
    If no MONDO match is found, include `MONDO ID': null` and an empty list for 'phenotypes'
    You must only return a valid (JSON block) list of GroundedDiseaseResult objects.  
    Do not include explanations, markdown formatting, or natural language in the JSON response 
    """
)

# Create grounding agent
grounding_agent = Agent(
    model= model,
    system_prompt=GROUNDING_SYSTEM_PROMPT,
    retries=3,
    output_type=List[GroundedDiseaseResult], # prints complete list of results. do not remove
)

# Register tools
grounding_agent.tool_plain(find_mondo_id)
grounding_agent.tool_plain(find_disease_knowledge)


















