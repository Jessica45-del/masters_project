"""
Agent 1 : Breakdown Agent
- Reads phenopackets
- Extracts HPO terms (ids) from phenopackets
- Returns a summary of clinical context:
    - HPO term → systems affected → initial candidate disease(s)
# """

from pydantic_ai import Agent
from multi_agent_system.agents.breakdown.shared_dependencies import model
from multi_agent_system.agents.breakdown.breakdown_tools import (
    list_phenopacket_files,
    load_phenopacket,
    extract_hpo_ids,
    render_prompt,
    call_model,
    parse_deepseek_response, save_result
)
# breakdown_agent.py
from multi_agent_system.agents.breakdown.shared_dependencies import model



# System prompt
BREAKDOWN_SYSTEM_PROMPT = (
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

# Create breakdown agent
breakdown_agent = Agent(
    model= model,
    system_prompt=BREAKDOWN_SYSTEM_PROMPT
)

# Register tools
breakdown_agent.tool_plain(list_phenopacket_files)
breakdown_agent.tool_plain(load_phenopacket)
breakdown_agent.tool_plain(extract_hpo_ids)
breakdown_agent.tool_plain(render_prompt)
breakdown_agent.tool_plain(call_model) #deepseek
breakdown_agent.tool_plain(parse_deepseek_response)

# Top-level planner that composes all steps
@breakdown_agent.tool_plain
def extract_phenopacket_pipeline(dir_path: str) -> list[str]:
    files = list_phenopacket_files(dir_path)
    saved: list[str] = []
    for fp in files:
        pkt    = load_phenopacket(fp)
        ids    = extract_hpo_ids(pkt)
        prompt = render_prompt(ids)
        raw    = call_model(prompt)
        parsed = parse_deepseek_response(raw)
        path   = save_result(parsed, fp)
        saved.append(path)
    return saved



# def extract_phenopacket_pipeline(ctx:RunContext[BreakdownAgentConfig], dir_path:str) -> list[dict]: