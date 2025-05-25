"""
Agent 1 : Breakdown Agent
- Reads phenopackets
- Extracts HPO terms (ids) from phenopackets
- Returns a summary of clinical context:
    - HPO term → systems affected → initial candidate disease(s)
# """
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext

from multi_agent_system.agents.breakdown.breakdown_config import BreakdownAgentConfig
from multi_agent_system.agents.breakdown.breakdown_tools import (
    list_phenopacket_files,
    load_phenopacket,
    extract_hpo_ids,
    render_prompt,
    call_model,
    parse_deepseek_response
)

cfg = BreakdownAgentConfig()

# System prompt
SYSTEM_PROMPT = (
    "You are an expert phenopacket diagnostic assistant."
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

#Intialise deepseek model and deepseek provider
model = OpenAIModel(
    'deepseek-chat',
    provider=DeepSeekProvider(api_key=cfg.api_key),
)

# Create breakdown agent
breakdown_agent = Agent(
    model="deepseek-r1",
    system_prompt=SYSTEM_PROMPT
)

# Register tools
breakdown_agent.tool(list_phenopacket_files)
breakdown_agent.tool(load_phenopacket)
breakdown_agent.tool(extract_hpo_ids)
breakdown_agent.tool(render_prompt)
breakdown_agent.tool_plain(call_model) #deepseek
breakdown_agent.tool(parse_deepseek_response)

# Top-level planner that composes all steps
@breakdown_agent.tool_plain
def extract_phenopacket_pipeline(ctx:RunContext[BreakdownAgentConfig], dir_path:str) -> list[dict]:
    files = list_phenopacket_files(dir_path)
    results = []
    for fp in files:
        pkt    = load_phenopacket(fp)
        ids    = extract_hpo_ids(pkt)
        prompt = render_prompt(ids)
        raw    = call_model(prompt)
        parsed = parse_deepseek_response(raw)
        results.extend(parsed)
    return results


