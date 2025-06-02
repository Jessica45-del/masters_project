"""
Agent for performing diagnostic reasoning
"""
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai import Agent
from multi_agent_system.agents.breakdown.shared_dependencies import model
from multi_agent_system.agents.breakdown.breakdown_tools import (
    list_phenopacket_files,
    prepare_prompt,
    extract_json_block,
    save_breakdown_result
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
    "Your role is to analyse clinical data from patient phenopackets."
    "When given a directory of phenopacket JSONs, follow these steps:"
    "1. list_phenopacket_files"
    "2. load_phenopacket"
    "3. extract_hpo_ids"
    "4. render_prompt"
    "5. call_deepseek" #change
    "6. parse_deepseek_response"
    "Return the parsed diagnostics as JSON format ."
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







