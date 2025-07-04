"""
Tools for Similarity Scoring Agent
"""

from typing import Set, List, Dict
from pydantic import BaseModel

from multi_agent_system.agents.breakdown.breakdown_tools import InitialDiagnosisResult
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import GroundedDiseaseResult

# Model output for similarity agent
class SimilarityScoreResult(BaseModel):
    disease_name:str # Candidate disease (from breakdown/grounding agent)")
    mondo_id:str | None # MONDO ID mapped to candidate disease
    similarity_score:float # calculated similarity score using Jaccard index . Comparing patient HPOs and disease HPOs (from similarity scoring agent)


# No need to re-extract HPO as this has already been done in cli, through extract hpo
# terms function from utils.py





# define jaccard index equation
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


# compute jaccard index for patient hpo_ids and hpo_ids associated with MONDO IDs (candidate diseases)
async def compute_similarity_scores(
    patient_hpo_ids: List[str],
    disease_hpo_map: Dict[str, List[str]],
    disease_names: Dict[str, str] #MONDO ID to disease name
) -> List[SimilarityScoreResult]:

    """
    Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs



    Args:
        patient_hpo_ids: List of patient HPO IDs
        disease_names: Dictionary mapping MONDO IDs to lists of HPO term IDs for each disease.
        disease_hpo_map: Dictionary mapping MONDO IDs to disease name (for readability)


        Returns:
            A List of SimilarityScoreResult objects in descending order of similarity score
    """
    patient_set = set(patient_hpo_ids)
    results = [] # store similarity results in a list

    # iterate of each disease
    for mondo_id, disease_hpos in disease_hpo_map.items():
        print("Disease:", mondo_id)
        print("HPO terms:", disease_hpos)

        disease_set = set(disease_hpos)
        score = calculate_jaccard_index(patient_set, disease_set)
        results.append(SimilarityScoreResult(
            disease_name=disease_names.get(mondo_id, "Unknown"),
            mondo_id=mondo_id,
            similarity_score=score
        ))

    return sorted(results, key=lambda x: x.similarity_score, reverse=True) #sort in descending order


# output for teh above
#
# results = [
#     SimilarityScoreResult(disease_name="A", mondo_id="MONDO:1", similarity_score=0.2),
#     SimilarityScoreResult(disease_name="B", mondo_id="MONDO:2", similarity_score=0.8),
#     SimilarityScoreResult(disease_name="C", mondo_id="MONDO:3", similarity_score=0.5),
# ]