"""
Tools for Breakdown Agent using Pydantic model for output.
"""

from typing import List
from pydantic import BaseModel, Field
from multi_agent_system.agents.breakdown.breakdown_config import get_config
from jinja2 import Environment, FileSystemLoader


class Phenotype(BaseModel):
    hpo_id: str = Field(..., description="HPO ID")
    hpo_term: str = Field(..., description="Phenotype label")
    organ_system_affected: str = Field(..., description="Affected system or organ")

class CandidateDisease(BaseModel):
    disease_name: str = Field(..., description="Disease label")


class InitialDiagnosisResult(BaseModel):
    phenotypes: List[Phenotype]
    candidate_diseases: List[CandidateDisease]



cfg = get_config()
_jinja_env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
_template = _jinja_env.get_template(cfg.template_file)


async def prepare_prompt(hpo_ids: List[str], sex: str) -> str:
    """
    Prepare diagnostic prompt by rendering HPO IDs and Sex.
    """

    print(f"[TOOL CALLED] prepare_prompt with hpo_ids={hpo_ids}, sex={sex}")
    prompt = _template.render(
        hpo_term=", ".join(hpo_ids),
        sex=sex
    )
    return prompt
