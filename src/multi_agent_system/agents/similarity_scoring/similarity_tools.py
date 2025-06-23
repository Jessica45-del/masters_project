"""
Tools for Similarity Scoring Agent
"""

from pathlib import Path
import json
from typing import Set, List, Dict


def get_patient_hpo_ids(file_path: str) -> Set[str]:
    """
    Retrieves the patient's observed phenotypes, i.e. HPO IDs from the breakdown agent
    output file.

    Args:
        file_path: Path to the initial_diagnosis JSON file.

    Returns:
        A set of HPO term IDs.
    """
    print(f"Loading HPO terms from: {file_path}")

    data = json.loads(Path(file_path).read_text())

    phenotypes = data[0].get("phenotypes", [])
    hpo_ids = {p["id"] for p in phenotypes if "id" in p}

    return hpo_ids


def calculate_jaccard_index(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity index between two sets.

    Args:
        set1: First set of HPO terms from patient
        set2: Second set of HPO terms disease profile (i.e. MONDO ID)

    Returns:
        Jaccard index (float between 0 and 1)
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 0.0

    return intersection / union


async def score_disease_candidates(
    patient_hpo: Set[str],
    candidates: List[Dict]
) -> List[Dict]:
    """
    Score candidate diseases using Jaccard similarity against patient HPOs.

    Args:
        patient_hpo: Set of HPO IDs from the patient
        candidates: List of disease dicts with 'id', 'label', 'phenotypes'

    Returns:
        List of candidate diseases with added similarity 'score'
    """
    results = []

    for disease in candidates:
        disease_hpos = {p["hpo_id"] for p in disease.get("phenotypes", [])}
        score = calculate_jaccard_index(patient_hpo, disease_hpos)

        results.append({
            "label": disease.get("label"),
            "id": disease.get("id"),
            "score": round(score, 4)
        })

    return results
