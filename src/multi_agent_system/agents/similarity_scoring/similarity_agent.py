"""
Similarity Scoring Agent.
"""
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import (
    SimilarityScoreResult, compute_similarity_scores,

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
    You are an assistant that specializes in rare disease similarity scoring.
    Your objective is to compute similarity between a patient's observed phenotypes 
    (HPO IDs) and a set of grounded disease candidates phenotype set ( i.e HPO IDs associated with 
    Each disease is annotated with a set of HPO terms describing its known phenotype profile.

    You will be provided:
    - `patient_hpo_ids`: a list of HPO terms observed in a patient.
      Example: ["HP:0000256", "HP:0000505"]

    - `disease_hpo_map`: a dictionary where each MONDO ID maps to a list of HPO terms.
      Example:
      {
        "MONDO:0015229": ["HP:0000256", "HP:0000505"],
        "MONDO:0008763": ["HP:0000556", "HP:0000618"]
      }

    - `disease_names`: a dictionary mapping MONDO IDs to disease names.
      Example:
      {
        "MONDO:0015229": "Bardet-Biedl syndrome",
        "MONDO:0008763": "Alström syndrome"
      }

    Perform the following steps:
    1. Use the `generate_similarity_scores` tool to compute similarity scores between the patient's HPO terms 
       and each disease.
       - This function expects `patient_hpo_ids`, `disease_hpo_map`, and `disease_names` as arguments.
       - It returns a list of `SimilarityScoreResult` objects, each containing a `mondo_id`, `disease_name`, 
         and `similarity_score`.

    2. Sort the results by similarity score in descending order (from highest to lowest).

    3. Return only the sorted list of `SimilarityScoreResult` objects in valid JSON format.
    
    Output rules:
    - Do NOT include any extra text, markdown, commentary, or explanations.
    - Output MUST be only a JSON array of `SimilarityScoreResult` objects.
    - Each object must include:
        - `mondo_id` (str)
        - `disease_name` (str)
        - `similarity_score` (float)
    """
)







# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT,
    output_type = List[SimilarityScoreResult]
)

#Register tools
similarity_agent.tool_plain(compute_similarity_scores)