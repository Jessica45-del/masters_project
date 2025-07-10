"""
Similarity Scoring Agent.
"""
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import (
    compute_similarity_scores,
    save_agent_results,

)
# Load configuration
config = get_config()

# Load LLM model
model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider(api_key=config.api_key),
)


SIMILARITY_SYSTEM_PROMPT = (
    """
    You are an assistant that specializes in rare disease similarity scoring and diagnosis.
    You task is to compute similarity between a patient's observed phenotypes (HPO IDs) 
    and disease candidate phenotype profiles,then return a prioritized list of the 9 most similar diseases in TSV format.
    You will receive:

    - `patient_hpo_ids`: a list of HPO term IDs for the patient.
    - `disease_hpo_map`: a dictionary mapping MONDO IDs to a list of HPO term IDs describing the disease.
    - `disease_names`: a dictionary mapping MONDO IDs to readable disease names.
    - `cosine_scores`: (optional) dictionary mapping MONDO IDs to cosine similarity scores.
    - `phenopacket_id`: the ID of the patient (used to name the output file).

    This is provided as arguments. You do not need to explicitly specify this argument.


    WORKFLOW- You MUST follow these steps in order:
    1. Use the compute_similarity_scores function compute the jaccard similarity scores between patient HPO IDs 
    and each HPO ID associated with the 9 candidate disease (or MONDO ID).
    2. Based on the cosine similarity score and jaccard similarity scores, you must use your 
    diagnostic reasoning to  rank the diseases from 1 (most likely) to 9 (least likely) 
    to be associated with the patient phenotype profiles.
    If both Jaccard and Cosine similarity scors are available, use both to inform ranking. 
    If only Jaccard scores are available, you must using those alone.
    You must ensure there are 9 candidate diseases from step 1 in the rank.
    4. You must assign a final score as the 1/rank for each candidate disease. For example, Rank 1 = 1.0, Rank 2 = 0.5 etc.
    5. You must call 'save_agent_results' function with the *exact list of dicts* returned from compute_similarity_scores 
    without changing its structure.
    
    Output Format:
    Again, You must return the output in TSV format using the save_agent_results function.
    
    ## Important Notes
    - You must call both `compute_similarity_scores` and `save_agent_results` functions to complete the objective.
    - You must focus on accuracy over explanation.
    -You must return a valid JSON response 
    - You must not return duplicate candidate disease
    - You must base rankings solely on similarity scores and clinical relevance.
    - DO NOT include any explanations, markdown, confirmation messages, or extra text.
    - Your response MUST NOT mention saving, success, or provide any instructions—
"""
)


# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT,
)

#Register tools
similarity_agent.tool_plain(compute_similarity_scores)
similarity_agent.tool_plain(save_agent_results)



# """
#
#  5. After ranking, you must call the save_agent_results providing:
#     - results: the ranked list of 9 SimilarityScoreResult objects
#     - phenopacket_id: the phenopacket patient identifier.
#     Use this when calling `save_agent_results`
# """