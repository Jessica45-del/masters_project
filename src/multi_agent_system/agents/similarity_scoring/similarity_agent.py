"""
Agent 3: Similarity scoring agent for diagnostic reasoning.
"""

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.similarity_scoring.similarity_tools import score_disease_candidates


# Load configuration (if needed)
config = get_config()

# Load LLM model
model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider(api_key=config.api_key),
)


SIMILARITY_SYSTEM_PROMPT =(
    """
    You are a diagnostic reasoning agent that compares patient phenotypes with candidate diseases.
    Your task is to:
    1. Compare the patient's HPO terms against the phenotype profiles of each candidate disease.
    2. Accept as input:
   - A list of patient HPO terms.
   - A list of disease candidates, where each candidate includes a MONDO ID, disease label, and associated HPO terms.
   3. Calculate the Jaccard similarity between the patient HPO set and each disease’s phenotype set.
   4. Return a list of candidate diseases, ranked in descending order of similarity.
   Each result must include:
   - `label`: the disease name
   - `id`: the MONDO identifier
   - `score`: the similarity score, rounded to 4 decimal places.

    """
)



# Create the agent
similarity_agent = Agent(
    model=model,
    system_prompt=SIMILARITY_SYSTEM_PROMPT
)

#Register tools
similarity_agent.tool_plain(score_disease_candidates)