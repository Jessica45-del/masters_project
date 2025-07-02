"""
MCP tools for interacting with the  Similarity Scoring Agent
"""
from typing import List, Dict, Set
from mcp.server.fastmcp import FastMCP

from multi_agent_system.agents.breakdown.breakdown_tools import InitialDiagnosisResult
from multi_agent_system.agents.grounding.grounding_tools import GroundedDiseaseResult
from multi_agent_system.agents.similarity_scoring.similarity_agent import SIMILARITY_SYSTEM_PROMPT
from multi_agent_system.agents.similarity_scoring.similarity_tools import SimilarityScoreResult, \
    generate_similarity_scores

# Initialise MCP server
mcp = FastMCP("similarity_scoring", instructions=SIMILARITY_SYSTEM_PROMPT)

@mcp.tool()
async def similarity_scores(
    initial_result: InitialDiagnosisResult,
    disease_candidates: List[GroundedDiseaseResult],
) -> List[SimilarityScoreResult]:
    """
    For each disease candidate, calculate the Jaccard similarity score between
    the patient HPO terms and the disease HPO terms, and return a list of results.

    Args:
        initial_result: InitialDiagnosisResult (from breakdown agent
        disease_candidates: List of GroundDiseaseResult (from grounding agent)

    Return:
        List of candidate diseases with similarity score

    """

    return await generate_similarity_scores(initial_result, disease_candidates) # need to determine the results are
