
from functools import lru_cache
from typing import List, Any
from oaklib import get_adapter
from oaklib.implementations import MonarchImplementation

from multi_agent_system.agents.breakdown.breakdown_tools import InitialDiagnosisResult
from multi_agent_system.utils.grounding_utils import search_mondo_fallback


from pydantic import BaseModel, Field

class GroundedDiseaseResult(BaseModel):
    disease_name: str = Field(..., description=" (Initial) Original disease label from breakdown agent")
    mondo_id: str | None = Field(None, description="Grounded MONDO ID, or None if not found")
    phenotypes:list = Field(default_factory=list, description="Phenotype/HPO association")


#reduce threshold

HAS_PHENOTYPE = "biolink:has_phenotype"

@lru_cache
def get_mondo_adapter():
    """ Retrieve the MONARCH ontology adapter

    Returns:
        The MONDO ontology adapter
        """
    return get_adapter("sqlite:obo:mondo")

# Extract disease labels from initial diagnosis files
async def ground_diseases(labels: List[str] ) -> list[GroundedDiseaseResult]:
    """
    Ground each candidate disease from the initial diagnosis result to a MONDO ID.

    Args:
        labels: list of disease names in candidate diseases

    Returns:
        A list of GroundedDisease entries with MONDO IDs or fallbacks
    """
    results = [] # collect grounded disease results with MONDO IDs
    for label in labels:
        grounding = await find_mondo_id(label)

        # if MONDO ID is found
        if "id" in grounding and grounding["id"]:
            results.append(GroundedDiseaseResult(
                disease_name=label,
                mondo_id=grounding["id"],
                fallback_reason=None
            ))

        # if no MONDO ID found
        else:
            results.append(GroundedDiseaseResult(
                disease_name=label,
                mondo_id=None,
                fallback_reason="No MONDO ID found via primary or fallback search"
            ))
    print (results)
    return results



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


async def find_disease_knowledge(mondo_id:str, limit: int =10 ) -> List[dict]:
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
           # predicates=[HAS_PHENOTYPE]
        )

        for i, assoc in enumerate(disease_association):
            if i >= 80: # limit number of HPO terms returned
                break
            if assoc.object:
                results.append({
                    "mondo_id": mondo_id,
                    "hpo_id": assoc.object,
                   # "predicate": getattr(assoc, "predicate", HAS_PHENOTYPE),
                   # "source": getattr(assoc, "provided_by", None),
                })


        return results

    except Exception as e:
        print(f"[ERROR] Failed to retrieve disease knowledge for {mondo_id}: {e}")
        return []
