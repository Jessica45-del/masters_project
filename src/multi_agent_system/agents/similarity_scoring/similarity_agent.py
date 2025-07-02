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
    generate_similarity_scores
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
    You will receive:
    - A patient's set of observed phenotypes (HPO term IDs), extracted from InitialDiagnosisResult.
    - A list of candidate diseases, each with a disease name, mapped MONDO ID, 
    and a list of associated HPO terms (from the grounding agent).
    Your task :
    1. For each disease candidate, you must compare the patient’s HPO terms to the disease’s phenotype set 
    using the Jaccard similarity index, using the 'generate_similarity_scores' function. 
    2. For each candidate, you must output:
    - `disease_name`: Disease label
    - `mondo_id`: MONDO identifier (or null if not found)
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
similarity_agent.tool_plain(generate_similarity_scores)