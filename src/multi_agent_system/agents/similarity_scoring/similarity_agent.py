"""
Similarity Scoring Agent.
"""

from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.openai import OpenAIProvider

from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import (
    compute_similarity_scores,
    SimilarityAgentOutput, save_agent_results,

)
# Load configuration
config = get_config()

# Load LLM model
model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider(api_key=config.api_key),
)

SIMILARITY_SYSTEM_PROMPT=(
    """
    You are an assistant that specializes in rare disease similarity scoring.
    
    WORKFLOW:
    1. You must  call the `compute_similarity_scores` function to calculate the jaccard index with:
    - Patient HPO IDs
    - Candidate diseases list (HPO terms)
    
    2. You must rank the candidate diseases based on similarity scores.
    3. You must call the `save_agent_results` function to save the ranked list in TSV format
    
    
    IMPORTANT:
    -You must only return a valid (JSON block) list of SimilarityAgentOutput objects.  
     -Do not include explanations, markdown formatting, or natural language in the JSON response 
    - DO NOT Add explanations
    - DO NOT Modify the input data
    - DO NOT Perform any other actions
    - You MUST call both functions exactly once, in order, and return the results from 'save_agents_results
    """
)


# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT,
    retries=5,
    output_type= SimilarityAgentOutput,
)

#Register tools
similarity_agent.tool_plain(compute_similarity_scores)
similarity_agent.tool_plain(save_agent_results)



