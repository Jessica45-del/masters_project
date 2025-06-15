"""
AGENT 1: Breakdown Agent for diagnostic reasoning
"""
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai import Agent
from multi_agent_system.agents.breakdown.breakdown_config import get_config
from multi_agent_system.agents.breakdown.breakdown_tools import (
   prepare_prompt,
   extract_json_block,
   save_breakdown_result, #list_phenopacket_files,
)

config = get_config()


#Define LLM model
model = OpenAIModel(
   "deepseek-chat",
   provider=DeepSeekProvider(api_key=config.api_key),
)

# System prompt
BREAKDOWN_SYSTEM_PROMPT = (
   "You are an expert diagnostic reasoning assistant."
   "Your role is to analyse clinical data from individual patient phenopacket files "
   "to generate an initial diagnosis."
   "You have access to a set of tools that enable you to complete this task step by step. "
   "For each patient phenopacket, follow the workflow below:"
   "1. Prepare the Diagnosis Prompt"
   "Use the prepare_prompt function to render the HPO IDs and sex into the prompt"
   "2. Generate diagnostic reasoning output"
   "The rendered prompt should be read by the model to generate an output"
   "Return your output as a JSON block containing the HPO id, labels, affected systems, and initial diagnosis "
   "3.Extract the JSON output"
   "Use the extract_json_block function to extract the JSON block of the output"
   "If the JSON cannot be parsed, return your fallback response indicating that the JSON could not be parsed"
   "4. Save the Initial Diagnosis Results "
   "Use the save_breakdown_result function to save the extracted JSON block into the initial_diagnosis subdirectory within "
   "the results directory."
   "The filename should correspond to the original patient file (e.g., `PatientA_initial_diagnosis.json`. "
   "'PatientB_initial_diagnosis.json')."
)

# Create breakdown agent
breakdown_agent = Agent(
   model= model,
   system_prompt=BREAKDOWN_SYSTEM_PROMPT
)

#Register tools
# breakdown_agent.tool_plain(list_phenopacket_files)
breakdown_agent.tool_plain(prepare_prompt)
breakdown_agent.tool_plain(extract_json_block)
breakdown_agent.tool_plain(save_breakdown_result)















