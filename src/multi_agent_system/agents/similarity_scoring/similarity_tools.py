"""
Tools for Similarity Scoring Agent
"""
import csv
from functools import lru_cache
from pathlib import Path
from typing import Set, List, Dict
from pydantic import BaseModel

from multi_agent_system.agents.breakdown.breakdown_tools import InitialDiagnosisResult
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config
from multi_agent_system.agents.grounding.grounding_tools import GroundedDiseaseResult



get_config()

# Model output for similarity agent
class SimilarityScoreResult(BaseModel):
    disease_name:str # Candidate disease (from breakdown/grounding agent)")
    mondo_id:str | None # MONDO ID mapped to candidate disease
    jaccard_similarity_score:float # calculated similarity score using Jaccard index . Comparing patient HPOs and disease HPOs (from similarity scoring agent)
    cosine_similarity_score:float | None

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
    disease_names: Dict[str, str], #MONDO ID to disease name
    cosine_scores: Dict[str, float | None] | None = None
) -> List[SimilarityScoreResult]:

    """
    Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs

    Args:
        patient_hpo_ids: List of patient HPO IDs
        disease_names: Dictionary mapping MONDO IDs to lists of HPO term IDs for each disease.
        disease_hpo_map: Dictionary mapping MONDO IDs to disease name (for readability)
        cosine_scores: Dictionary of cosine similarity scores of diseases, where MONDO id was not found through basic search

    Returns:
        A List of SimilarityScoreResult objects in descending order of similarity score
    """
    print("[TOOL CALLED]Computing similarity scores")
    cosine_scores = cosine_scores or {}
    patient_set = set(patient_hpo_ids)
    results = [] # store similarity results in a list

    # iterate of each disease
    for mondo_id, disease_hpos in disease_hpo_map.items():
        print("Candidate disease Mondo ID :", mondo_id) # mondo ID mapped to candidate disease
        print("Associated HPO terms:", disease_hpos)

        disease_set = set(disease_hpos)
        score = calculate_jaccard_index(patient_set, disease_set)
        print(f"DEBUG: mondo_id={mondo_id}, cosine_scores.get(cosine_score)={cosine_scores.get(mondo_id)}")

        results.append(SimilarityScoreResult(
            disease_name=disease_names.get(mondo_id, "Unknown"),
            mondo_id=mondo_id,
            jaccard_similarity_score=score,
            cosine_similarity_score=cosine_scores.get(mondo_id # get score for disease
        )))

    return sorted(results, key=lambda x: x.jaccard_similarity_score, reverse=True) #sort  jaccard index score (only) in descending order


# save final prioritised list of candidate diseases
# @lru_cache
async def save_agent_results(results: List[SimilarityScoreResult], phenopacket_id: str, output_dir: Path = Path("agent_result")) -> None:
    """
    Save final list of ranked disease to agent_results folder

    Args:
        results: List of SimilarityScoreResult objects in descending order of similarity score
        output_dir: Path to output (agent_results)  folder
        phenopacket_id: patient identifier that is used to name the tsv file.
    """

    print("[TOOL CALLED]Saving agent results")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{phenopacket_id}-agents.tsv"

    print(f"[INFO] Writing results to: {output_path.resolve()}")

    try:
        with output_path.open("w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(["Rank", "Score", "Disease", "MONDO_ID"])

            for rank, result in enumerate(results, start=1):
                score = round(1 / rank, 4)
                writer.writerow([rank, score, result.disease_name, result.mondo_id])

        print(f"[SUCCESS] Results successfully saved to: {output_path.name}")
    except IOError as e:
        print(f"[ERROR] Failed to write results: {e}")
        raise

