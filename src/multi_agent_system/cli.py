import asyncio
import click
from pathlib import Path

from pheval.utils.file_utils import all_files

from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.agents.similarity_scoring.similarity_agent import similarity_agent
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex


@click.group()
def cli():
    """Multi-Agent System CLI for Rare Disease Diagnosis"""
    pass


@cli.command()
@click.option('--phenopacket-dir', type=click.Path(exists=True), required=True, help='Directory with phenopacket JSON files')
async def run_breakdown(phenopacket_dir: str):
    """Run only the breakdown agent (HPO → initial candidate diseases)"""
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")

        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        breakdown_input = f"""
        Patient case: {phenopacket_path.stem}
        HPO terms: {hpo_ids}
        Patient sex: {sex}

        Please provide initial diagnosis.
        """

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        response = await breakdown_agent.run(hpo_ids=hpo_ids, sex=sex)
        print(f"[BREAKDOWN RESULT]:\n{response.output}\n")


@cli.command(name="run_pipeline")
@click.option('--phenopacket-dir', type=click.Path(exists=True), required=True, help='Directory with phenopacket JSON files')
def run_pipeline(phenopacket_dir: str):
    """Run full pipeline: Breakdown → Grounding"""
    asyncio.run(run_pipeline_async(phenopacket_dir))

async def run_pipeline_async(phenopacket_dir: str):
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")
        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        # BREAKDOWN AGENT
        breakdown_input = f"""
        Patient case: {phenopacket_path.stem}
        HPO terms: {hpo_ids}
        Patient sex: {sex}
    
        """
        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        print(breakdown_result)

        # GROUNDING AGENT
        candidate_labels = [d.disease_name for d in breakdown_result.output.candidate_diseases] #extract candidate disease name from InitialDiagnosisResult
        print("candidate_labels:", candidate_labels)
        grounding_results = await grounding_agent.run(candidate_labels)
        print("Type of grounding_results.output:", type(grounding_results.output))
        print("Value:", grounding_results.output)

        print("[GROUNDING RESULT]:")
        for result in grounding_results.output:
            print(result)
        print()

        print("DEBUG: grounding_results.output =", grounding_results.output)
        print("DEBUG: grounding_results.output just after grounding agent =", grounding_results.output)

        # SIMILARITY SCORE AGENT
        print("[SIMILARITY SCORING AGENT]:")
        similarity_results = await similarity_agent.run(
            initial_result = breakdown_result.output,
            disease_candidates = grounding_results.output,
        )
        print("Type of similarity_results.output:", type(similarity_results.output))
        print("Value:", similarity_results.output) # view raw results
        for sim_result in similarity_results.output:
            print(sim_result)
        print()


if __name__ == "__main__":
    cli()
