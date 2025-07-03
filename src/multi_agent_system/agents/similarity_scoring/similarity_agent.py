"""
Similarity Scoring Agent.
"""
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import (
    SimilarityScoreResult,
    generate_similarity_scores, extract_patient_hpo_ids, extract_disease_hpo_ids, calculate_jaccard_index
)
# Load configuration
config = get_config()

# Load LLM model
model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider(api_key=config.api_key),
)


SIMILARITY_SYSTEM_PROMPT =(
    """
    You are a diagnostic reasoning agent specialising in rare disease similarity scoring.
    You must complete the follow tasks:
    1. You must extract the patient hpo id from InitialDiagnosisResult using the extract_patient_hpo_ids function.
    2.You must extract the hpo id from GroundedDiseaseResult using the extract_disease_hpo_ids function.
    3.For each disease candidate, you must compare the patient’s HPO terms to the disease’s phenotype set 
    using the Jaccard similarity index, using the 'generate_similarity_scores' function. 
    4. For each candidate, you must output:
    - `disease_name`: Disease label
    - `mondo_id`: MONDO ID (or null if not found)
    - `disease_phenotypes`: List of associated HPO terms for that disease
    - `similarity_score`: The similarity score (float, between 0 and 1), rounded to 4 decimal places.
    Important:
    - Only return a **list of SimilarityScoreResult objects** (as JSON). 
    Do not include explanations, markdown, or any extra text.
    """
)



# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT,
    output_type = List[SimilarityScoreResult]
)

#Register tools
similarity_agent.tool_plain(extract_patient_hpo_ids)
similarity_agent.tool_plain(extract_disease_hpo_ids)
similarity_agent.tool_plain(calculate_jaccard_index)
similarity_agent.tool_plain(generate_similarity_scores)