"""
AGENT 1: Breakdown Agent for diagnostic reasoning
"""
from typing import List

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai import Agent

from multi_agent_system.agents.breakdown.breakdown_config import get_config
from multi_agent_system.agents.breakdown.breakdown_tools import (
   prepare_prompt,
   InitialDiagnosisResult,
)

config = get_config()


#Define LLM model
model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)




BREAKDOWN_SYSTEM_PROMPT = ("""
You are an expert diagnostic reasoning assistant specializing in rare disease diagnosis.
You will receive patient cases with HPO (Human Phenotype Ontology) IDs and patient sex.
Your task is to analyze this phenotypic data and provide an initial diagnostic assessment.

WORKFLOW - You MUST follow these steps in order:
1. Use the prepare_prompt function to render the HPO IDs and sex into a structured diagnostic prompt
2. Based on the rendered prompt, analyze the phenotypic evidence and generate your diagnostic reasoning
3. You must return a valid structured response that conforms exactly to the InitialDiagnosisResult model
The workflow is only complete when you call the save_breakdown_result function.

OUTPUT FORMAT:
You must return the output based on the InitialDiagnosisResult model

IMPORTANT NOTES:
- You must return a valid JSON response 
- You must not return duplicate candidate diseases 
- DO NOT include any explanations, markdown, confirmation messages, or extra text.
- Your response MUST NOT mention saving, success, or provide any instructions—only the JSON object!
"""
)

# Create breakdown agent
breakdown_agent = Agent(
   model= model,
   system_prompt=BREAKDOWN_SYSTEM_PROMPT,
   output_type=InitialDiagnosisResult
)



#Register tools
breakdown_agent.tool_plain(prepare_prompt)
















