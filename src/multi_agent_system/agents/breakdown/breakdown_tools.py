"""
Tools for Breakdown Agent
"""

from pathlib import Path
import json
import re
from jinja2 import Environment, FileSystemLoader
from pheval.utils.phenopacket_utils import phenopacket_reader, PhenopacketUtil
from multi_agent_system.agents.breakdown.breakdown_config import get_config

# Load config and Jinja2 environment
cfg = get_config()
_jinja_env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
_template = _jinja_env.get_template(cfg.template_file)


async def list_phenopacket_files(phenopacket_dir: str) -> list[str]:
    """Return all phenopacket files (.json) file paths in the phenopacket directory

    Args:
    dir_path: Path to the phenopacket directory

    Returns:
        Phenopacket files in phenopacket directory
    """
    print("Searching in phenopacket_dir:", Path(phenopacket_dir).resolve())
    return [str(p) for p in Path(phenopacket_dir).glob("*.json")]


async def prepare_prompt(file_path: str) -> tuple[str, str]:
    """
    Load a phenopackets, extract HPO ID  and metadata (sex and PMID)
    and render a prompt.

    Args:
        file_path: Path to the phenopacket JSON file

    Returns:
        The prompt and phenopacket file name .
    """
    print(f"Loading phenopacket file: {file_path}")

    # Load phenopacket as an object
    phenopacket = phenopacket_reader(Path(file_path))

    # Extract HPO term IDs
    hpo_ids = [p.type.id for p in PhenopacketUtil(phenopacket).observed_phenotypic_features()]

    # Extract patient metadata
    sex = phenopacket.subject.sex.value if phenopacket.subject and phenopacket.subject.sex else "UNKNOWN"
    pkt_id = phenopacket.id or "UNKNOWN"

    # Render the template using your diagnosis prompt (global jinja template)
    prompt = _template.render(
        hpo_terms=", ".join(hpo_ids),
        sex=sex,
        id=pkt_id
    )

    # Return the prompt and filename base (for saving results)
    return prompt, Path(file_path).stem


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
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return [{"error": "Could not parse JSON"}, {"raw": text}]


async def save_breakdown_result(data: list[dict], name: str) -> Path:
    """
    Save results to J

    Args:
        data: JSON response from deepseek model
        name: Name of patient file

    Returns:
        A JSON output file with the patient HPO IDs, phenotype (label), systems affects
       and initial diagnosis
    """
    path = cfg.output_dir / f"{name}_initial_diagnosis.json"
    path.write_text(json.dumps(data, indent=2))
    return path


