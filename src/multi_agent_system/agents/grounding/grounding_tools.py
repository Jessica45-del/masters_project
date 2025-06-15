import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any, Coroutine
from oaklib import get_adapter



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

    Returns:
        A dictionary mapping each patient file name to the intial candidates diseases
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
async def find_mondo_id(label:str) -> dict[str, str | Any] | dict[str, str | None]:
    """
    Search for MONDO ID for a given patient disease label and return the best match.

    Args:
        label: The disease label to search (e.g."Bardet-Biedl syndrome(BBS)")

    Returns:
        A dictionary with the disease 'label' and 'MONDO ID', or 'id':None if not found
    """
    print(f"Searching for {label}")
    adapter = get_mondo_adapter()

    try:
        results = adapter.basic_search(label)
        if results:
            hit = results[0]
            print(f"[DEBUG] Found match: {hit.id} ({hit.label})")
            return {"label": label, "id": hit.id}
    except Exception as e:
        print(f"[ERROR] Failed to ground '{label}': {e}")

    return {"label": label, "id": None}

# async def get_disease_profile():


