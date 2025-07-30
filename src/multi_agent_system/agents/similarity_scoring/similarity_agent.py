"""
Similarity Scoring Agent.
"""

from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider


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
    1. You must  call the `compute_similarity_scores` function with:
    - Patient HPO IDs
    - Candidate diseases list
    
    2. Review the cosine similarity and jaccard similarity score in SimilarityAgentOutput object.
        - for each phenopacket ID consider you must use your own reasoning to rank the candidate list 
    
    2. You must call the `save_agent_results` function with:
    - the results from `compute_similarity_scores`
    - the phenopacket ID
    3. You must return 9 candidate diseases. 
    

    IMPORTANT:
    -You must only return a valid JSON block list of SimilarityAgentOutput objects.  
     -Do not include explanations, markdown formatting, or natural language in the JSON response 
    - DO NOT Add explanations
    - DO NOT Modify the input data
    - NOT Perform any other actions
    - You MUST call both functions exactly once, in order, and return the results from 'save_agents_results
    """
)

# SIMILARITY_SYSTEM_PROMPT = (
#         """
#         You are an assistant that specializes in rare disease similarity scoring and rare disease diagnosis.
#         Your task is to compute jaccard similarity between a patient's observed phenotypes (HPO IDs)
#         and a list of candidate disease phenotype profiles (this is the HPO ID terms associated with a MONDO ID)
#
#
#
#         WORKFLOW — You MUST follow these steps in order:
#
#         1. You MUST call 'compute_similarity_score' to calculate jaccard similarity score.
#         2. You MUST return the exact output from `compute_similarity_scores` based on the SimilarityAgentOutput object
#         You must complete these two tasks before moving on to another task.
#         3. Save the results using the save_agent_results function.
#
#
#         Output Format:
#         -You must return the original disease 'disease_name'
#         -You must return the MONDO ID 'mondo_id
#         -You must return the jaccard similarity score 'jaccard_similarity_score'
#         -You must return cosine_similarity_score 'cosine_similarity_score' , this may be null
#         -
#
#         IMPORTANT NOTE:
#         - You MUST call `compute_similarity_scores` function
#         - Do not include explanations, markdown formatting, or natural language.
#         - You MUST NOT mention saving, success, or status messages
#         - You MUST focus strictly on accurate scoring and ranking
# """
# )


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



