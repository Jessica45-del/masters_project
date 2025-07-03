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
    # score: float = Field(..., description="Reciprocal rank score")

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

# -----------------------------------
# Extract Pydantic Model from LLM Output
# ---------------------------------
# async def extract_json_block(text: str) -> InitialDiagnosisResult:
#     """
#     Extract JSON object and validate against Breakdown Diagnosis model.
#
#     Args:
#         text (str): Text to be parsed containing the JSON object representing initial diagnosis.
#
#     Returns:
#         Validated Breakdown Diagnosis model containing the extracted data
#     """
#     print(f"[TOOL CALLED] extract_json_block {text}")
#
#     match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
#     if not match:
#         match = re.search(r"({.*})", text, re.DOTALL)
#     if not match:
#         raise ValueError("No model block found")
#     try:
#         parsed = json.loads(match.group(1))
#         return InitialDiagnosisResult.model_validate(parsed)
#     except (json.JSONDecodeError, ValidationError) as e:
#         raise ValueError(f"Could not parse or validate model: {e}")
#
#
# # ------------------------------
# #  Save Model Result
# # ------------------------------
# async def save_breakdown_result(
#     model: InitialDiagnosisResult,
#     name: str
# ) -> Path:
#     """
#     Save validated BreakdownDiagnosis as JSON.
#     """
#     print(f"[TOOL CALLED] save_breakdown_result with name={name}")
#     output_path = cfg.output_dir / f"{name}.json"
#     output_path.write_text(model.model_dump_json(indent=2))
#     return output_path
