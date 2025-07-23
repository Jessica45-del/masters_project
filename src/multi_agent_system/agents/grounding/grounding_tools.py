"""Tools for Grounding agent"""
import asyncio
from functools import lru_cache
from typing import List, Any, Dict
from oaklib import get_adapter
from oaklib.implementations import MonarchImplementation
from multi_agent_system.utils.grounding_utils import cosine_similarity
from pydantic_ai import ModelRetry
from pydantic import BaseModel, Field


class GroundedDiseaseResult(BaseModel):
    disease_name: str = Field(..., description="(Initial) Original disease label from breakdown agent")
    mondo_id: str | None = Field(None, description="Grounded MONDO ID, or None if not found")
    phenotypes: List[str] = Field(
        default_factory=list,
        description="List of HPO IDs associated with the disease")
    cosine_score: float | None = Field(None, description="Cosine similarity score")


HAS_PHENOTYPE = "biolink:has_phenotype"


@lru_cache
def get_mondo_adapter():
   """ Retrieve the MONARCH ontology adapter


   Returns:
       The MONDO ontology adapter
       """
   return get_adapter("sqlite:obo:mondo")


async def ground_diseases(labels: List[str]) -> list[GroundedDiseaseResult]:
    """
    Ground each candidate disease from the initial diagnosis result to a MONDO ID.


    Args:
       labels: list of disease names in candidate diseases


    Returns:
       A list of GroundedDisease entries with MONDO IDs or fallbacks
    """

    try:
        results = []
        for label in labels:
            try:
                grounding = await find_mondo_id(label)
                print(f"\n[DEBUG] Grounding result for '{label}': {grounding}")

                if "id" in grounding and grounding["id"]:
                    results.append(GroundedDiseaseResult(
                        disease_name=label,
                        mondo_id=grounding["id"],
                        cosine_score=grounding.get("cosine_score"),
                        fallback_reason=None
                    ))
                else:
                    results.append(GroundedDiseaseResult(
                        disease_name=label,
                        mondo_id=None,
                        cosine_score=grounding.get("cosine_score"),
                        fallback_reason="No MONDO ID found via primary or fallback search"
                    ))
            except Exception as e:
                error_msg = f"Failed to ground disease '{label}': {e}"
                print(f"[ERROR] {error_msg}")
                results.append(GroundedDiseaseResult(
                    disease_name=label,
                    mondo_id=None,
                    cosine_score=None,
                    fallback_reason=error_msg
                ))

        return results
    except Exception as e:
        error_msg = f"Systemic failure in ground_diseases: {e}"
        print(f"[CRITICAL] {error_msg}")
        raise ModelRetry(error_msg) from e


async def find_mondo_id(label: str) -> Dict[str, Any]:
    """
    Search for MONDO ID for a given patient disease label and return the best match.


    Args:
       label: The candidate disease label to search (e.g."Bardet-Biedl syndrome(BBS)")


    Returns:
       A dictionary with the disease 'label' and 'MONDO ID', or 'id':None if not found
    """

    try:
        print(f"Searching for MONDO ID for label: {label}")
        adapter = get_mondo_adapter()

        try:
            results = list(adapter.basic_search(label))
            mondo_results = [r for r in results if str(r).startswith("MONDO:")]

            if mondo_results:
                hit = mondo_results[0]
                print(f"[Exact Match] Found MONDO ID: {hit}")
                return {"label": label, "id": hit}
        except Exception as e:
            print(f"[WARNING] Exact search failed for '{label}': {e}")

        # Fallback to cosine similarity
        return cosine_similarity(label)
    except Exception as e:
        error_msg = f"Failed to find MONDO ID for '{label}': {e}"
        print(f"[ERROR] {error_msg}")
        raise ModelRetry(error_msg) from e



async def find_disease_knowledge(mondo_id: str, limit: int = 80) -> List[str]:
    """"
    Retrieve disease knowledge for a given MONDO ID.


    Arg:
       mondo_id: The MONDO ID to retrieve knowledge


    Returns:
       List of dictionaries with HPO terms and other disease associated metadata
    """
    try:
        print(f"Retrieve disease knowledge for {mondo_id}")
        adapter = MonarchImplementation()
        results = []
        disease_association = adapter.associations(subjects=[mondo_id])

        for i, assoc in enumerate(disease_association):
            if i >= limit:
                break
            if assoc.object:
                results.append(assoc.object)
        return results
    except Exception as e:
        error_msg = f"Failed to retrieve disease knowledge for {mondo_id}: {e}"
        print(f"[ERROR] {error_msg}")
        raise ModelRetry(error_msg) from e





















# async def find_disease_knowledge(mondo_id: str, limit: int = 80) -> List[dict]:
#     """"
# Retrieve disease knowledge for a given MONDO ID.
#
#
# Arg:
#    mondo_id: The MONDO ID to retrieve knowledge
#
#
# Returns:
#    List of dictionaries with HPO terms and other disease associated metadata
# """
#
#     try:
#         print(f"Retrieve disease knowledge for {mondo_id}")
#         adapter = MonarchImplementation()
#         results = []
#         disease_association = adapter.associations(subjects=[mondo_id])
#
#         for i, assoc in enumerate(disease_association):
#             if i >= limit:
#                 break
#             if assoc.object:
#                 results.append({
#                     "mondo_id": mondo_id,
#                     "hpo_id": assoc.object,
#                 })
#         return results
#     except Exception as e:
#         error_msg = f"Failed to retrieve disease knowledge for {mondo_id}: {e}"
#         print(f"[ERROR] {error_msg}")
#         raise ModelRetry(error_msg) from e







