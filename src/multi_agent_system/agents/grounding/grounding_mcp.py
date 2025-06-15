"""
MCP tools for Grounding Agent
"""
from pathlib import Path
from typing import Dict, List

from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.grounding.grounding_agent import GROUNDING_SYSTEM_PROMPT
from multi_agent_system.agents.grounding.grounding_tools import extract_disease_label, find_mondo_id
from multi_agent_system.agents.grounding.grounding_config import GroundingAgentConfig
#Initialise MCP sever
mcp = FastMCP("grounding", instructions=GROUNDING_SYSTEM_PROMPT)


@mcp.tool()
async def get_disease_label(results_dir:str ) -> Dict[str, List[str]]:
    """Extract candidate disease labels from initial_diagnosis result files

     Args:
        results_dir: The directory containing the initial diagnosis results

    Returns:
        A dictionary to maps each filename stem to the disease labels
     """

    return await extract_disease_label()


@mcp.tool()
async def get_mondo_id(label:str) -> Dict[str, List[str]]:
    """
    Search for MONDO ID for a given patient disease label
    
    Args:
        label: The disease label to search 
        
    Returns:
        A dictionary that maps disease label to MONDO ID
    """
    return await find_mondo_id()




if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')