"""
MCP tools for Breakdown Agent
"""

from typing import  List
from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.breakdown.breakdown_agent import BREAKDOWN_SYSTEM_PROMPT
from multi_agent_system.agents.breakdown.breakdown_tools import (

    prepare_prompt,
    # extract_json_block,
    # save_breakdown_result,
    InitialDiagnosisResult,
)

mcp = FastMCP("breakdown", instructions=BREAKDOWN_SYSTEM_PROMPT) #breakdown agent and breakdown system prompt



@mcp.tool()
async def construct_diagnosis_prompt(hpo_ids: List[str], sex: str) -> str:
    """
    Prepare prompt

    Args:
        hpo_ids: List of hpo ids
        sex: Patient sex

    Returns:

    """
    prompt = await prepare_prompt(hpo_ids, sex)
    return prompt



if __name__ == "__main__":
   # initialise and run the server
   mcp.run(transport="stdio") # serving layer



