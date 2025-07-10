"""
Similarity Scoring Agent.
"""
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import (
    SimilarityScoreResult, compute_similarity_scores, save_agent_results,

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
    You are an assistant that specializes in rare disease similarity scoring and rare disease diagnosis.
    Your objectives are to compute similarity between a patient's observed phenotypes (HPO IDs) and a set of grounded disease
    candidates phenotype set ( i.e HPO IDs associated with MONDO ID (disease candidate)) and use this ranking to provide 
    a final prioritised list of candidate diseases associated with the patient phenotypic profile 
    - Each disease is annotated with a set of HPO terms describing its known phenotype profile.

    You will receive the following input data as function arguments:

    - `patient_hpo_ids`: List[str] – HPO terms from the patient's phenopacket.
    - `disease_hpo_map`: Dict[str, List[str]] – mapping from MONDO ID to disease HPO terms.
    - `disease_names`: Dict[str, str] – mapping from MONDO ID to readable disease name. You must return 9 disease names 
    - `cosine_scores`: Dict[str, float or None] – mapping from MONDO ID to cosine similarity scores (if available).

    Do not fabricate diseases or use any hardcoded examples. 
    Always compute similarity only using the provided arguments.
    
    Perform the following steps:
    1. You must use the `compute_similarity_scores` function to calculate similarity scores 
       - This function expects `patient_hpo_ids`, `disease_hpo_map`, `disease_names` and cosine_scores as arguments 
       (the cosine_score may be null and this is still valid)
       You must use the 'compute_similarity_score to calculate the jaccard similarity score. 
       You must not attempt to calculate jaccard similarity manually
       - You must return a list of `SimilarityScoreResult` objects, each containing a `mondo_id`, `disease_name`, 
       `jaccard_similarity_score` and 'cosine_similarity_score'.

    2. You must use the available similarity scores form the list of `SimilarityScoreResult` objects to 
    rank these diseases based on which is most likely to be the causing the patient phenotypic profile.  
     - If both `jaccard_score` and `cosine_score` are available, use both to inform ranking.
     - If only `jaccard_score` is available, rank using that alone.
     - You must provide the rank from 1 (most likely) to 9 (least likely)
    
    3. After calling `compute_similarity_scores`, you will receive a full list of scored diseases.
    You must:
    - Sort the list using both Jaccard and cosine similarity (when available), using your reasoning.
    - Truncate the list to the top 9 most similar diseases.
    - Assign a final score of 1/rank for each (1.0 for first, 0.5 for second, etc.)
    - Pass that list to `save_agent_results` and also return it.
    4. You must assign a final score to each disease as the reciprocal of its rank (1 for the top-ranked
    disease, 0.5 the second, etc.).
    
    5. After ranking, you must call the save_agent_results providing:
    - results: the ranked list of 9 SimilarityScoreResult objects
    - phenopacket_id: the phenopacket patient identifier. 
    Use this when calling `save_agent_results`.
    
    The output TSV header must be Rank\tScore\tDisease\tMONDO ID ("The output TSV must include the following
    tab-separated columns: Rank, Score, Disease, MONDO ID.)
        
    Important notes :
    You must call both compute_similarity_scores function and save_agent_results function.
    You do not need to explain your reasoning, you need to be as specific as possible, 
    the goal is to get the correct answer. 
    You do not need to give any reasoning, just list the predicted diseases.
    The output must be a valid JSON array of objects (not a string, not markdown, no commentary).
    You must return a TSV file using the 'save_agent_results' function. 
    """
)


# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT,
    output_type = SimilarityScoreResult
)

#Register tools
similarity_agent.tool_plain(compute_similarity_scores)
similarity_agent.tool_plain(save_agent_results)