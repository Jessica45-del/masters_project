"""
Multi-Component Protocol (MCP) entrypoint for breakdown agent
MCP tools for performing initial diagnostic breakdown.
"""

from mcp.server.fastmcp import FastMCP
from pydantic_ai import RunContext

from multi_agent_system.agents.breakdown.breakdown_tools import (
    extract_phenopacket,
    initial_candidate_diseases,
)
from multi_agent_system.agents.breakdown.breakdown_config import get_config, BreakdownDependencies
from multi_agent_system.agents.breakdown.breakdown_agent import BREAKDOWN_SYSTEM_PROMPT

# Initialise FastMCP server with system instructions

mcp = FastMCP("breakdown", instructions=BREAKDOWN_SYSTEM_PROMPT)

ctx = RunContext[BreakdownDependencies](deps=get_config())

@mcp.tool()
async def run_extract_phenopacket(phenopacket_path: str):
    """Run HPO extraction from one phenopacket"""
    return await extract_phenopacket(ctx, phenopacket_path)

@mcp.tool()
async def run_initial_candidates(phenopacket_path: str):
    """Run clinical summarisation and candidate inference"""
    return await initial_candidate_diseases(ctx, phenopacket_path)

if __name__ == "__main__":
    mcp.run(transport="stdio")
