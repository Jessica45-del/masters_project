"""
AGENT 1: Breakdown Agent for diagnostic reasoning
"""
from typing import List

from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai import Agent

from multi_agent_system.agents.breakdown.breakdown_config import get_config
from multi_agent_system.agents.breakdown.breakdown_tools import (
   prepare_prompt,
   extract_json_block,
   save_breakdown_result,
)


config = get_config()


#Define LLM model
model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)




BREAKDOWN_SYSTEM_PROMPT = ("""
You are an expert diagnostic reasoning assistant specializing in rare disease diagnosis.
You will receive patient cases with HPO (Human Phenotype Ontology) term IDs and patient sex.
Your task is to analyze this phenotypic data and provide an initial diagnostic assessment.

WORKFLOW - You MUST follow these steps in order:
1. Use the prepare_prompt function to render the HPO IDs and sex into a structured diagnostic prompt
2. Based on the rendered prompt, analyze the phenotypic evidence and generate your diagnostic reasoning
3. Create a JSON response with your analysis
4. Use the extract_json_block function to validate your JSON output against the PhenotypeDiagnosisResult model
5. Use the save_breakdown_result function to save the results to the initial_diagnosis subdirectory located 
in the results directory 
The workflow is only complete when you call the save_breakdown_result function.

OUTPUT FORMAT:
-You must return the output based on the AgentBreakdownResult model 


IMPORTANT NOTES:
- Always use the tools in the specified sequence
- Handle cases where exact disease matching is not possible
- DO NOT include any explanations, markdown, confirmation messages, or extra text.
- Your response MUST NOT mention saving, success, or provide any instructions—only the JSON object!
- The filename for saved results should be {patient_name}_initial_diagnosis.json
- Your response MUST NOT mention saving, success, or provide any instructions—only the JSON object!
"""
)
class AgentBreakdownResult(BaseModel):
   hpo_id: List[str]
   phenotypes: List[str]
   systems_affected = List[str]
   initial_diagnosis:List[str]

# Create breakdown agent
breakdown_agent = Agent(
   model= model,
   system_prompt=BREAKDOWN_SYSTEM_PROMPT,
   output_type=AgentBreakdownResult
)



#Register tools
breakdown_agent.tool_plain(prepare_prompt)
breakdown_agent.tool_plain(extract_json_block)
breakdown_agent.tool_plain(save_breakdown_result)















