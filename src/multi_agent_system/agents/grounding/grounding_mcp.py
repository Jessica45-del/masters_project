"""
MCP tools for interacting with the  Grounding Agent
"""

from typing import Dict, List
from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.grounding.grounding_agent import GROUNDING_SYSTEM_PROMPT
from multi_agent_system.agents.grounding.grounding_tools import (
    find_mondo_id,
    find_disease_knowledge,
)


#Initialise MCP sever
mcp = FastMCP("grounding", instructions=GROUNDING_SYSTEM_PROMPT)


@mcp.tool()
async def get_mondo_id(label:str) -> Dict[str, List[str]]:
    """
    Search for MONDO ID for a given patient disease label
    
    Args:
        label: The disease label to search 
        
    Returns:
        A dictionary that maps disease label to MONDO ID
    """
    return await find_mondo_id(label)


@mcp.tool()
async def get_disease_knowledge(mondo_id:str) -> List[dict]:
    """
    Retrieve disease knowledge for a given MONDO ID.

    Args:
        mondo_id: Mondo ID to retrieve knowledge

    Returns:
        List of mondo IDs with associated disease knowledge
    """
    return await find_disease_knowledge(mondo_id)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')