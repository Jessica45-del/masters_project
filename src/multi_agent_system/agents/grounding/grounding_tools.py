# from oaklib.implementations import MonarchImplementation
# Tools for retrieval of external information from the Monarch KB and MONDO (oaklib)
# Extract HPO terms from Agent 1 output in initial diagnosis file for Monarch queries
## tool to communicate handoff from agent  1 to agent 2?
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from oaklib import get_adapter
from pydantic_ai import RunContext

from multi_agent_system.agents.grounding.grounding_config import GroundingAgentConfig, get_config


@lru_cache
def get_mondo_adapter():
    """ Retrieve the MONARCH ontology adapter

    Returns:
        The MONDO ontology adapter
        """
    return get_adapter("sqlite:obo:mondo")

# Extract disease labels from initial diagnosis files
async def extract_disease_label(results_dir:str ) -> Dict[str, List[str]]:
    """
    Extract candidate disease labels from initial_diagnosis result files

    Args:
    results_dir: The directory containing the initial diagnosis results

    Returns: A dictionary mapping each patient file name to its list of candidates diseases

    """
    result = {}
    input_dir = Path(results_dir)
    for file_path in input_dir.glob("*.json"):
        try:
            data = json.loads(file_path.read_text())
            if isinstance(data, list) and "candidate_diseases" in data[0]:
                labels = data[0]["candidate_diseases"]
                result[file_path.stem] = labels
            else:
                print(f"Invalid or missing candidate_diseases in {file_path.name}")
        except Exception as e:
            print(f"Failed to read {file_path.name}: {e}")
    return result

# Search for MONDO ID
async def find_mondo_id(
        ctx: RunContext[GroundingAgentConfig],
        label:str
) -> Dict:
    """
    Search for MONDO ID for a given patient disease label and return the best match.

    Args:
        ctx: run context
        label: The disease label to search (e.g."Bardet-Biedl syndrome")

    Returns:
        A dictionary with the disease 'label' and 'MONDO id', or 'id':None if not found
    """
    print(f"Searching for {label}")
    config = ctx.deps or GroundingAgentConfig()
    adapter = config.mondo_adapter

    try:
        results = adapter.basic_search(label)
        if results:
            hit = results[0]
            return {"label": label, "id": hit.id}
    except Exception as e:
        print(f"[ERROR] Failed to ground '{label}': {e}")

    return {"label": label, "id": None}

# async def get_disease_profile():


