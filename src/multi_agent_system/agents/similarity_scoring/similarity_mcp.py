"""
MCP tools for interacting with the  Similarity Scoring Agent
"""
from typing import List, Dict, Set
from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.similarity_scoring.similarity_agent import SIMILARITY_SYSTEM_PROMPT
from multi_agent_system.agents.similarity_scoring.similarity_tools import score_disease_candidates


# Initialise MCP server
mcp = FastMCP("similarity_scoring", instructions=SIMILARITY_SYSTEM_PROMPT)

@mcp.tool()
async def score_disease_candidates(patient_hpo: Set[str],
    candidates: List[Dict]
) -> List[Dict]:
    """
    Score candidate diseases using Jaccard index

    Args:
        patient_hpo: Set of HPO IDs from the patient
        candidates: List of disease dicts with 'id', 'label', 'phenotypes'

    Return:
        List of candidate diseases with similarity score

    """

    return await score_disease_candidates(patient_hpo, candidates)
