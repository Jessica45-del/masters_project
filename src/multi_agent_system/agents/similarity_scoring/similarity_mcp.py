"""
MCP tools for interacting with the  Similarity Scoring Agent
"""
from pathlib import Path
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.similarity_scoring.similarity_agent import SIMILARITY_SYSTEM_PROMPT
from multi_agent_system.agents.similarity_scoring.similarity_tools import save_agent_results, SimilarityAgentOutput
from multi_agent_system.agents.similarity_scoring.similarity_tools import compute_similarity_scores

# Initialise MCP server
mcp = FastMCP("similarity_scoring", instructions=SIMILARITY_SYSTEM_PROMPT)


@mcp.tool()
async def calculate_similarity_scores(
    patient_hpo_ids: List[str],
    candidate_diseases: List[Dict]
) -> SimilarityAgentOutput:
    """
    Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs

    Args:
        patient_hpo_ids: List of HPO IDs
        candidate_diseases: List of dictionaries, each representing a candidate disease

    Returns:
        SimilarityAgentOutput

    """

    print("[DEBUG] candidate_diseases received by MCP tool:", candidate_diseases)

    return await compute_similarity_scores(patient_hpo_ids, candidate_diseases)



@mcp.tool()
async def save_final_results(results: List[dict], phenopacket_id: str, output_dir: Path = Path("agent_results")) \
        -> None:
    """
    Save finalised prioritised list of ranked diseases to agent_results folder

   Args:
       results: List of dicts representing similarity scores
       phenopacket_id: patient identifier that is used to name the tsv file
       output_dir: Path to output (agent_results) folder

    """

    return await save_agent_results(results, phenopacket_id, output_dir)


if __name__ == "__main__":
   # initialise and run the server
   mcp.run(transport="stdio") # serving layer
