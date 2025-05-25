from pathlib import Path
import json, re
from jinja2 import Environment, FileSystemLoader
from multi_agent_system.agents.breakdown.breakdown_config import BreakdownAgentConfig
from multi_agent_system.agents.breakdown.shared_dependencies import model, config

# Load configuration & template once
defaults = BreakdownAgentConfig()
_jinja_env = Environment(loader=FileSystemLoader(str(defaults.template_dir)))
_template  = _jinja_env.get_template(defaults.template_file)


def list_phenopacket_files(dir_path: str) -> list[str]:
    """Return all phenopackets (.json) file paths in the given directory."""
    return [str(p) for p in Path(dir_path).glob("*.json")]


def load_phenopacket(file_path: str) -> dict:
    """Read and parse a single Phenopacket JSON file."""
    read_phenopacket = Path(file_path).read_text(encoding="utf-8")
    return json.loads(read_phenopacket)


def extract_hpo_ids(phenopacket: dict) -> list[str]:
    """Extract all HPO IDs from phenotypicFeatures section in phenopacket."""
    features = phenopacket.get("phenotypicFeatures", [])
    return [feat["type"]["id"] for feat in features if feat.get("type", {}).get("id")]


def render_prompt(hpo_ids: list[str]) -> str:
    """Insert (Render) the Jinja2 prompt (template) HPO terms."""
    return _template.render(hpo_terms=", ".join(hpo_ids))


def call_model(prompt: str) -> str:
    """Invoke Deepseek via the pydantic-ai model."""
    return model.complete(
        prompt=prompt,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
    )


def parse_deepseek_response(content: str) -> list[dict]:
    """Extract the JSON block from ```json ... ``` and parse it into Python data."""
    m = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", content)
    if not m:
        raise ValueError("Expected JSON block in ```json ... ```")
    return json.loads(m.group(1))



def save_result(parsed: list[dict], input_path: str) -> str:
    """Save parsed output to initial_diagnosis/<filename>_diagnosis.json."""
    out_dir = defaults.output_dir
    out_dir.mkdir(exist_ok=True)
    base = Path(input_path).stem
    out_path = out_dir / f"{base}_diagnosis.json"
    out_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
    return str(out_path)
