"""Tools for Similarity Scoring Agent"""
import csv
from functools import lru_cache
from pathlib import Path
from typing import Set, List, Dict, Optional, Any
from pydantic_ai import ModelRetry
from pydantic import BaseModel
from multi_agent_system.agents.similarity_scoring.similarity_config import get_config


class SimilarityScoreResult(BaseModel):
    disease_name: str
    mondo_id: Optional[str]
    jaccard_similarity_score: float
    cosine_similarity_score: Optional[float]


class SimilarityAgentOutput(BaseModel):
    results: List[SimilarityScoreResult]

def calculate_jaccard_index(set1: Set[str], set2: Set[str]) -> float:
    """
       Calculate Jaccard similarity index between two sets.


       Args:
           set1: First set of HPO terms from patient
           set2: Second set of HPO terms disease profile (i.e. MONDO ID)


       Returns:
           Jaccard index (float between 0 and 1)
       """

    try:
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        # print(
        #     f"[DEBUG] Jaccard calculation - Intersection: {intersection}, Union: {union}, Score: {intersection / union if union > 0 else 0.0}")
        return intersection / union if union > 0 else 0.0
    except Exception as e:
        error_msg = f"Jaccard calculation failed: {e}"
        print(f"[ERROR] {error_msg}")
        raise ModelRetry(error_msg) from e


async def compute_similarity_scores(
        patient_hpo_ids: List[str],
        candidate_diseases: List[Dict[str, Any]],
) -> SimilarityAgentOutput:
    try:
        print("[TOOL CALLED] Computing Jaccard Index!")
        patient_set = set(patient_hpo_ids)
        results = []

        for disease in candidate_diseases:
            try:
                disease_name = disease["disease_name"]
                mondo_id = disease.get("mondo_id")
                raw_phenotypes = disease.get("phenotypes", [])
                cosine_score = disease.get("cosine_score")

                # Handle different phenotype types
                if isinstance(raw_phenotypes, set):
                    phenotypes = list(raw_phenotypes)  # Convert set to list
                elif isinstance(raw_phenotypes, str):
                    phenotypes = [raw_phenotypes]  # Wrap string in list
                else:
                    phenotypes = raw_phenotypes  # Assume it's already a list

                disease_set = set(phenotypes)  # Now safe
                jaccard_score = calculate_jaccard_index(patient_set, disease_set)

                results.append(SimilarityScoreResult(
                    disease_name=disease_name,
                    mondo_id=mondo_id,
                    jaccard_similarity_score=jaccard_score,
                    cosine_similarity_score=cosine_score,
                ))
            except Exception as e:
                print(f"[ERROR] Failed to process disease '{disease.get('disease_name', 'unknown')}': {e}")

        return SimilarityAgentOutput(results=results)
    except Exception as e:
        error_msg = f"Failed to compute similarity scores: {e}"
        print(f"[CRITICAL] {error_msg}")
        raise ModelRetry(error_msg) from e


async def save_agent_results(results: List[dict], phenopacket_id: str,
                             output_dir: Path = Path("agent_results")) -> None:
    """
      Save final list of ranked disease to agent_results folder


      Args:
          results: List of dicts representing similarity scores.
          output_dir: Path to output (agent_results)  folder
          phenopacket_id: patient identifier that is used to name the tsv file.
      """

    try:
        print("[TOOL CALLED] Saving agent results")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{phenopacket_id}-agents.tsv"

        try:
            with output_path.open("w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(["Rank", "Score", "Candidate Disease", "MONDO_ID"])

                for rank, result in enumerate(results, start=1):
                    try:
                        score = round(1 / rank, 4)
                        writer.writerow([rank, score, result["disease_name"], result["mondo_id"]])
                    except Exception as e:
                        print(f"[ERROR] Failed to write result row {rank}: {e}")
        except Exception as e:
            error_msg = f"File operation failed for {output_path}: {e}"
            print(f"[ERROR] {error_msg}")
            raise ModelRetry(error_msg) from e

        print(f"[SUCCESS] Results saved to: {output_path.name}")
    except Exception as e:
        error_msg = f"Failed to save agent results: {e}"
        print(f"[CRITICAL] {error_msg}")
        raise ModelRetry(error_msg) from e






#
# async def compute_similarity_scores(
#         patient_hpo_ids: List[str],
#         candidate_diseases: List[Dict[str, Any]],
# ) -> SimilarityAgentOutput:
#     """
#     Compute similarity scores between patient HPO IDs and each candidate disease (or MONDO ID) HPO IDs
#
#     Args:
#         patient_hpo_ids: List of patient HPO IDs
#         candidate_diseases: List of dicts. Each include:
#             - disease_name: str
#             - mondo_id: str
#             - phenotypes: List [str]
#             - cosine_score: float |None
#
#     Returns:
#         A list of disease ranked by Jaccard index/score, each as a dictionary
#     """
#
#     try:
#         print("[TOOL CALLED] Computing Jaccard Index!")
#         patient_set = set(patient_hpo_ids)
#         results = []
#
#         for disease in candidate_diseases:
#             try:
#                 disease_id = disease.get("mondo_id") or disease["disease_name"]
#                 disease_name = disease["disease_name"]
#                 disease_phenotypes = disease.get("phenotypes", [])
#                 cosine_score = disease.get("cosine_score")
#
#                 disease_set = set(disease_phenotypes)
#                 jaccard_score = calculate_jaccard_index(patient_set, disease_set)
#
#                 results.append(SimilarityScoreResult(
#                     disease_name=disease_name,
#                     mondo_id=disease.get("mondo_id"),
#                     jaccard_similarity_score=jaccard_score,
#                     cosine_similarity_score=cosine_score,
#                 ))
#             except Exception as e:
#                 print(f"[ERROR] Failed to process disease '{disease.get('disease_name', 'unknown')}': {e}")
#
#         # sorted_results = sorted(results, key=lambda x: x.jaccard_similarity_score, reverse=True)[:10]
#
#         return SimilarityAgentOutput(results=results)
#     except Exception as e:
#         error_msg = f"Failed to compute similarity scores: {e}"
#         print(f"[CRITICAL] {error_msg}")
#         raise ModelRetry(error_msg) from e