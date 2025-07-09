"""
MCP tools for interacting with the  Similarity Scoring Agent
"""
from pathlib import Path
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.similarity_scoring.similarity_agent import SIMILARITY_SYSTEM_PROMPT
from multi_agent_system.agents.similarity_scoring.similarity_tools import SimilarityScoreResult, save_agent_results
from multi_agent_system.agents.similarity_scoring.similarity_tools import compute_similarity_scores

# Initialise MCP server
mcp = FastMCP("similarity_scoring", instructions=SIMILARITY_SYSTEM_PROMPT)


@mcp.tool()
async def calculate_similarity_scores(
        patient_hpo_ids: List[str],
        disease_hpo_map: Dict[str, List[str]],
        disease_names: Dict[str, str], #MONDO ID to disease name
        cosine_scores: Dict[str, float | None] | None = None
) -> List[SimilarityScoreResult]:

    """
    Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs


    Args:
        patient_hpo_ids: List of patient HPO IDs
        disease_names: Dictionary mapping MONDO IDs to lists of HPO term IDs for each disease.
        disease_hpo_map: Dictionary mapping MONDO IDs to disease name (for readability)
        cosine_scores: Dictionary mapping MONDO IDs to cosine similarity scores.
    Returns:
        A List of SimilarityScoreResult objects in descending order of similarity score
    """

    return await compute_similarity_scores(patient_hpo_ids=patient_hpo_ids,
                                           disease_hpo_map=disease_hpo_map,
                                           disease_names=disease_names,
                                           cosine_scores=cosine_scores)

@mcp.tool()
async def save_agent_results(results: List[SimilarityScoreResult],phenopacket_id: str, output_dir: Path = Path("agent_result")) \
        -> None:
    """
    Save finalised prioritised list of ranked diseases to agent_results folder

   Args:
       results: List of SimilarityScoreResult objects in descending order of similarity score
       phenopacket_id: patient identifier that is used to name the tsv file
       output_dir: Path to output (agent_results) folder

    """

    return await save_agent_results(results, phenopacket_id, output_dir)