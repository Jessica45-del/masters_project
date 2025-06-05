"""
AGENT 2:
Grounding agent for retrieval of external data that is part of the multi-system
diagnostic reasoning agent
"""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.openai import OpenAIProvider


model = OpenAIModel(
    model_name="deepseek-chat",
    provider=DeepSeekProvider()
)

GROUNDING_SYSTEM_PROMPT(
    "You are an expert in rare disease knowledge."
    "Your task is to provide additional ontological information about rare disease"
    "You will perform this task by completing the following steps:"
    "1) Map HPO ID (terms) to MONDO disease IDs"
    "2) Retrieve disease knowledge using MONDO IDs "
    "You will map the HPO ID (terms) to MONDO IDs by using the find_mondo_disease_id function"
    "and you will return as a list in JSON format"
    "You will retrieve disease knowledge using MONDO IDs by using the get_disease_profile function"
    "and you will return as a list in JSON format"
    ""
)



# Create grounding agent
grounding_agent = Agent(
   model= model,
   system_prompt=GROUNDING_SYSTEM_PROMPT
)

# Register tools



















