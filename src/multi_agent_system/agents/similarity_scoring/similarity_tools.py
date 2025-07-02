"""
Tools for Similarity Scoring Agent
"""

from typing import Any, Set, List, Dict
from pydantic import BaseModel
from multi_agent_system.agents.breakdown.breakdown_tools import InitialDiagnosisResult
from multi_agent_system.agents.grounding.grounding_tools import GroundedDiseaseResult


class SimilarityScoreResult(BaseModel):
    disease_name:str # Candidate disease (from breakdown/grounding agent)")
    mondo_id:str | None # MONDO ID mapped to candidate disease
    disease_phenotypes:List[dict] # HPO terms associated with MONDO ID (from grounding agent)
    similarity_score:float # calculated similarity score using Jaccard index . Comparing patient HPOs and disease HPOs (from similarity scoring agent)
   #rank: int | None = None


def normalize_hpo_terms(phenotypes: List[Any]) -> Set[str]:
    """Normalize a list of HPO phenotypes, whether dicts or strings, to a set of HPO IDs.

    Args:
        phenotypes: List of HPO terms from patient

    Return:
        A set of HPO IDs as strings

    """
    result = set()
    for p in phenotypes:
        if isinstance(p, dict) and "hpo_id" in p:
            result.add(p["hpo_id"])
        elif isinstance(p, str):
            result.add(p)
        # If it's a Pydantic object, adapt as needed
        elif hasattr(p, "hpo_term"):
            result.add(p.hpo_term)
    return result

def ensure_phenotype_dict_list(phenotypes: list) -> list[dict]:
    """
    Ensure a list of dicts, converting strings to dicts with hpo_id as key.
    Required for SimilarityScoreResult pydantic model.
    """
    result = []
    for p in phenotypes:
        if isinstance(p, dict):
            result.append(p)
        elif isinstance(p, str):
            result.append({"hpo_id": p})
        # Optionally, support for Pydantic objects
        elif hasattr(p, "hpo_term"):
            result.append({"hpo_id": p.hpo_term})
    return result



# extract patient hpo terms
def extract_patient_hpo_terms(result:InitialDiagnosisResult) -> set[str]:
    return set (p.hpo_term for p in result.phenotypes)

# extract disease hpo terms
def extract_disease_hpo_terms(candidate:GroundedDiseaseResult) -> Set[str]:
    hpo_terms = set()
    for p in candidate.phenotypes:
        if isinstance(p, dict) and "hpo_id" in p:
            hpo_terms.add(p["hpo_id"])
        elif isinstance(p, str):
            hpo_terms.add(p)
    return hpo_terms


# computer similarity score
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

    return intersection / union if union > 0 else 0.0


async def generate_similarity_scores(
    initial_result: InitialDiagnosisResult,
    disease_candidates: List[GroundedDiseaseResult],
) -> List[SimilarityScoreResult]:
    
    """
    For each disease candidate, calculate the Jaccard similarity score between
    the patient HPO terms and the disease HPO terms, and return a list of results.

    Args:
        initial_result: The InitialDiagnosisResult (from patient breakdown agent output)
        disease_candidates: List of GroundedDiseaseResult (from grounding agent)

    Returns:
        List of SimilarityScoreResult for each candidate disease.
    """
    print("Received disease_candidates:", disease_candidates)
    patient_hpo_terms = extract_patient_hpo_terms(initial_result)
    results = []

    for candidate in disease_candidates:
        print("Processing candidate:", candidate.disease_name, candidate.phenotypes)
        disease_hpo_terms = extract_disease_hpo_terms(candidate)
        score = calculate_jaccard_index(patient_hpo_terms, disease_hpo_terms)
        normalized_phenos = ensure_phenotype_dict_list(candidate.phenotypes)
        print("Normalized candidate phenotypes:", normalized_phenos)
        result = SimilarityScoreResult(
            disease_name=candidate.disease_name,
            mondo_id=candidate.mondo_id,
            disease_phenotypes=normalized_phenos,
            similarity_score=score,
        )
        results.append(result)
        print("Returning similarity results:", results)

    return results

