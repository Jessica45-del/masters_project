"""
Tools for Similarity Scoring Agent
"""
import csv
from functools import lru_cache
from pathlib import Path
from typing import Set, List, Dict, Optional, Union, Any, Coroutine

from pydantic import BaseModel
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config




get_config()

# Model output for similarity agent

class SimilarityScoreResult(BaseModel):
    disease_name: str
    mondo_id: Optional[str]
    jaccard_similarity_score: float
    cosine_similarity_score: Optional[float]


class SimilarityAgentOutput(BaseModel):
    results: List[SimilarityScoreResult]

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

    print(
        f"[DEBUG] Jaccard calculation — Intersection: {intersection}, Union: {union}, Score: {intersection / union if union > 0 else 0.0}")

    return intersection / union if union > 0 else 0.0


# compute jaccard index for patient hpo_ids and hpo_ids associated with MONDO IDs (candidate diseases)

async def compute_similarity_scores(
    patient_hpo_ids: List[str],
    candidate_diseases: List[Dict[str,Any]], #more flexible typing
) -> SimilarityAgentOutput:

    """
    Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs

    Args:
        patient_hpo_ids: List of patient HPO IDs
        candidate_diseases: List of dicts. Each include:
            - disease_name: str
            - mondo_id: str
            - phenotypes: List [str]
            - cosine_score: float |None

    Returns:
        A list of disease ranked by Jaccard index/score, each as a dictionary
    """
    print("[TOOL CALLED] Computing Jaccard Index!")



    patient_set = set(patient_hpo_ids)


    # ===== DEBUGG LOGGGING =====
    print(f"[DEBUG] Patient HPO IDs received: {patient_set}")
    if candidate_diseases:
        first_candidate = candidate_diseases[0]
        print(f"[DEBUG] First candidate disease: {first_candidate['disease_name']}")
        print(f"[DEBUG] First candidate's HPOs: {set(first_candidate.get('phenotypes', []))}")
    print(f"[DEBUG] Total candidates received: {len(candidate_diseases)}")


    results = []


    for disease in candidate_diseases:
        disease_id = disease.get("mondo_id") or disease["disease_name"] # get mondo id, fallback to disease name if not
        disease_name = disease["disease_name"]
        disease_phenotypes = disease.get("phenotypes", []) # get HPO terms associated with candidate disease
        cosine_score= disease.get("cosine_score") # get cosine score, may be none if not provided

        disease_set = set(disease_phenotypes)
        jaccard_score = calculate_jaccard_index(patient_set,disease_set)

        results.append(SimilarityScoreResult(
            disease_name=disease_name,
            mondo_id=disease.get("mondo_id"),
            jaccard_similarity_score=jaccard_score,
            cosine_similarity_score=cosine_score,

        ))


        print(f"[DEBUG] Processing disease: {disease['disease_name']}")
        print(f"[DEBUG] Phenotypes: {disease.get('phenotypes')}")

    return SimilarityAgentOutput(results=sorted(results, key=lambda x: x.jaccard_similarity_score, reverse=True)[:10])


# save final prioritised list of candidate diseases


async def save_agent_results(results: List[dict], phenopacket_id: str, output_dir: Path = Path("agent_results")) -> None:
    """
    Save final list of ranked disease to agent_results folder

    Args:
        results: List of dicts representing similarity scores.
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
            writer.writerow(["Rank", "Score", "Candidate Disease", "MONDO_ID"])

            for rank, result in enumerate(results, start=1):
                score = round(1 / rank, 4)
                writer.writerow([rank, score, result["disease_name"], result["mondo_id"]])


        print(f"[SUCCESS] Results successfully saved to: {output_path.name}")
    except IOError as e:
        print(f"[ERROR] Failed to write results: {e}")
        raise

