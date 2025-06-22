"""
Tools for Breakdown Agent
"""

from pathlib import Path
import json
import re
from typing import Tuple, List
from jinja2 import Environment, FileSystemLoader
from multi_agent_system.agents.breakdown.breakdown_config import get_config



# Load config and Jinja2 environment
cfg = get_config()
_jinja_env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
_template = _jinja_env.get_template(cfg.template_file)


# Prepare prompt
async def prepare_prompt(hpo_ids: List[str], sex: str) -> str:
    """
    Prepare diagnostic prompt by rendering HPO IDs and Sex

    Args:
        hpo_ids: List of HPO term IDs
        sex: Patient sex

    Returns:
        Rendered prompt
    """
    prompt = _template.render(
        hpo_terms=", ".join(hpo_ids),
        sex=sex
    )
    return prompt



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


