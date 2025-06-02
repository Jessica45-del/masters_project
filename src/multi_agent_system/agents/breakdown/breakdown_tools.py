"""
Tools for Breakdown Agent
"""

from pathlib import Path
import json, re
from jinja2 import Environment, FileSystemLoader
from pheval.utils.phenopacket_utils import phenopacket_reader, PhenopacketUtil
from multi_agent_system.agents.breakdown.breakdown_config import get_config

# Load config and Jinja2 environment
cfg = get_config()
_jinja_env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
_template = _jinja_env.get_template(cfg.template_file)


async def list_phenopacket_files(phenopacket_dir: str) -> list[str]:
    """Return all phenopacket files (.json) file paths in the phenopacket directory

# Load configuration & template once
defaults = BreakdownAgentConfig()
_jinja_env = Environment(loader=FileSystemLoader(str(defaults.template_dir)))
_template  = _jinja_env.get_template(defaults.template_file)

    Returns:
        Phenopacket files in phenopacket directory
    """
    print("Searching in phenopacket_dir:", Path(phenopacket_dir).resolve())
    return [str(p) for p in Path(phenopacket_dir).glob("*.json")]

def list_phenopacket_files(dir_path: str) -> list[str]:
    """Return all phenopackets (.json) file paths in the given directory."""
    return [str(p) for p in Path(dir_path).glob("*.json")]

async def prepare_prompt(file_path: str) -> tuple[str, str]:
    """
    Load a phenopackets, extract HPO ID  and metadata (sex and PMID)
    and render a prompt.

def load_phenopacket(file_path: str) -> dict:
    """Read and parse a single Phenopacket JSON file."""
    read_phenopacket = Path(file_path).read_text(encoding="utf-8")
    return json.loads(read_phenopacket)

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

def call_model(prompt: str) -> str:
    """Invoke Deepseek via the pydantic-ai model."""
    return model.complete(
        prompt=prompt,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
    )


async def save_breakdown_result(data: list[dict], name: str) -> Path:
    """
    Save results to J




