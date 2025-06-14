"""
Tools for Breakdown Agent
"""

from pathlib import Path
import json
import re
from typing import Tuple

from jinja2 import Environment, FileSystemLoader
from multi_agent_system.agents.breakdown.breakdown_config import get_config
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex


# Load config and Jinja2 environment
cfg = get_config()
_jinja_env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
_template = _jinja_env.get_template(cfg.template_file)


# Prepare prompt
async def prepare_prompt( file_path: Path) -> Tuple[str, str]:
    """
    Prepare prompt inserting HPO id and sex into the prompt

    Arg:
        file_path: file path to phenopacket json file

    Returns:
        Rendered prompt and phenopacket file path
    """
    print(f"Loading phenopacket file: {file_path}")

    # Path to phenopacket files
    file_path_obj = Path(file_path)

    # Extract HPO ID and sex using extract_hpo_ids_and_sex() in utils.py
    hpo_ids, sex = extract_hpo_ids_and_sex(file_path_obj)

    print(f"Extracting HPO ids: {hpo_ids}")
    print(f"Extracted Sex: {sex}")

    # Render prompt
    prompt = _template.render(
        hpo_terms=", ".join(hpo_ids),
        sex=sex
    )

    return prompt, file_path_obj.stem


async def extract_json_block(text: str) -> list[dict]:
   """
   Extract JSON block from deepseek model response

   Args:
       text: Deepseek model response

   Returns:
       JSON block from deepseek model response.
       If JSON could not be parsed, return an error message "Could not parse JSON"
   """
   match = re.search(r"```json\s*(\[\s*{.*?}\s*])\s*```", text, re.DOTALL)
   if match:
       try:
           parsed = json.loads(match.group(1))
           if isinstance(parsed, list):
               return parsed
       except json.JSONDecodeError as e:
           print(f"[DEBUG] JSON decode error: {e}")
   return [{"error": "Could not parse JSON"}, {"raw": text}]



async def save_breakdown_result(data: list[dict], name: str) -> Path:
   """
   Save results the results to

   Args:
       data: JSON response from deepseek model
       name: Name of patient file

   Returns:
       A JSON output file with the patient HPO IDs, phenotype (label), systems affects
      and initial diagnosis
   """
   output_path = cfg.output_dir / f"{name}_initial_diagnosis.json"
   output_path.write_text(json.dumps(data, indent=2))
   return output_path





# async def run_breakdown_pipeline(file_path: str) -> tuple[list[dict], str]:
#     """
#     Run the breakdown pipeline for one phenopacket.
#
#     Args:
#         file_path: Path to JSON files in the phenopackets directory
#
#     Returns:
#         Parsed diagnosis result and phenopacket file base name.
#     """
#     prompt, name = await prepare_prompt(file_path)
#     print(f"[Breakdown] Prompt ready for: {name}")
#     response = await model.complete(prompt=prompt)
#     parsed = await extract_json_block(response)
#     print(f"[Breakdown] Diagnosis complete for: {name}")
#     return parsed, name
