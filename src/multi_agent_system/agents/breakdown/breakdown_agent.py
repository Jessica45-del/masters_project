"""
Agent for performing diagnostic reasoning
"""
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai import Agent


from multi_agent_system.agents.breakdown.breakdown_config import get_config
from multi_agent_system.agents.breakdown.breakdown_tools import (
   list_phenopacket_files,
   prepare_prompt,
   extract_json_block,
   save_breakdown_result,
)

config = get_config()


#Define LLM model
model = OpenAIModel(
   "deepseek-r1",
   provider=DeepSeekProvider(api_key=config.api_key),
)

# System prompt
BREAKDOWN_SYSTEM_PROMPT = (
   "You are an expert diagnostic reasoning assistant."
   "Your role is to analyse clinical data from patient phenopackets."
   "Your workflow is as follows:"
   "1. List phenopacket files using list_phenopacket_file function"
   "2. Load phenopackets and extract HPO ID/term, sex and PMID,"
   "then insert into the prompt using prepare_prompt function"
   "3. Extract the json block from model (deepseek) output using extract_json_block function."
   "   If there is no JSON block return could not parse JSON"
   "4. Save the results in the initial_diagnosis sub-directory in the results directory"
)

# Create breakdown agent
breakdown_agent = Agent(
   model= model,
   system_prompt=BREAKDOWN_SYSTEM_PROMPT
)

# Register tools
breakdown_agent.tool_plain(list_phenopacket_files)
breakdown_agent.tool_plain(prepare_prompt)
breakdown_agent.tool_plain(extract_json_block)
breakdown_agent.tool_plain(save_breakdown_result)















