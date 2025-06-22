import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any
from oaklib import get_adapter
from oaklib.implementations import MonarchImplementation

from multi_agent_system.utils.grounding_utils import search_mondo_fallback

HAS_PHENOTYPE = "biolink:has_phenotype"


@lru_cache
def get_mondo_adapter():
    """ Retrieve the MONARCH ontology adapter

    Returns:
        The MONDO ontology adapter
        """
    return get_adapter("sqlite:obo:mondo")

# Extract disease labels from initial diagnosis files
async def extract_disease_label(file_path:str) -> Dict[str, List[str]]:
    """
    Extract candidate disease labels from initial_diagnosis result files

    Args:
    results_dir: The directory containing the initial diagnosis results

    Returns:
        A dictionary mapping each patient file name to the intial candidates diseases
    """
    print(f"[DEBUG] extract_disease_label called with file: {file_path}")
    result = {}

    try:
        data = json.loads(Path(file_path).read_text())
        if isinstance(data, list) and "candidate_diseases" in data[0]:
            labels = [d["label"] for d in data[0]["candidate_diseases"] if "label" in d]
            result[Path(file_path).stem] = labels
            print(f"[DEBUG] Extracted labels: {result}")
        else:
            print(f"[WARN] No candidate_diseases in {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to read: {file_path}: {e}")

    return result



# Search for MONDO ID
async def find_mondo_id(label:str) -> dict[str, str | Any] | dict[str, str | None]:
    """
    Search for MONDO ID for a given patient disease label and return the best match.

    Args:
        label: The candidate disease label to search (e.g."Bardet-Biedl syndrome(BBS)")

    Returns:
        A dictionary with the disease 'label' and 'MONDO ID', or 'id':None if not found
    """
    print(f"Searching for MONDO ID for label: {label}")
    adapter = get_mondo_adapter()

    try:
        results = list(adapter.basic_search(label))
        if results and not isinstance(results[0], str):
            hit = results[0]
            print(f"Found match: {hit.id}")
            return {"label": label, "id": hit.id}
    except Exception as e:
        print(f"Failed to ground '{label}': {e}")

    # Fallback to cosine similarity if exact (i.e. basic search) match fails
    return search_mondo_fallback(label)


async def find_disease_knowledge(mondo_id:str) -> List[dict]:
    """
    Retrieve disease knowledge for a given MONDO ID.

    Arg:
        mondo_id: The MONDO ID to retrieve knowledge

    Returns:
        List of dictionaries with HPO terms and other disease associated metadata
    """
    print(f"Retrieve disease knowledge for {mondo_id}")
    adapter = MonarchImplementation()

    try:
        results = []
        disease_association = adapter.associations(
            subjects=[mondo_id],
            predicates=[HAS_PHENOTYPE]
        )

        for assoc in disease_association:
            if assoc.object:
                results.append({
                    "mondo_id": mondo_id,
                    "hpo_id": assoc.object,
                    "predicate": getattr(assoc, "predicate", HAS_PHENOTYPE),
                    "source": getattr(assoc, "provided_by", None),
                })

        return results

    except Exception as e:
        print(f"[ERROR] Failed to retrieve disease knowledge for {mondo_id}: {e}")
        return []
