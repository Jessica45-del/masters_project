import asyncio
import click
from pathlib import Path

from pheval.utils.file_utils import all_files

from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex
from multi_agent_system.agents.similarity_scoring.similarity_tools import compute_similarity_scores


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
        HPO ids: {hpo_ids}
        Patient sex: {sex}

        Please provide initial diagnosis.
        """

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        print("[RUNNING BREAKDOWN AGENT]")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        print(f"[BREAKDOWN RESULT]:\n{breakdown_result}\n")  # breakdown_result.output = InitialDiagnosisResult

#  poetry run agents run_pipeline --phenopacket-dir multi_agent_system/phenopackets

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
        print("[RUNNING BREAKDOWN AGENT]")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        print(f"[BREAKDOWN RESULT]:\n{breakdown_result}\n") # breakdown_result.output = InitialDiagnosisResult


        # GROUNDING AGENT
        # extract candidate disease name from InitialDiagnosisResult
        # breakdown_result.output is the InitialDiagnosisResult object

        print("[RUNNING GROUNDING AGENT]")
        candidate_disease_labels = [d.disease_name for d in breakdown_result.output.candidate_diseases]

        print("candidate_disease_labels:", candidate_disease_labels)
        grounding_results = await grounding_agent.run(candidate_disease_labels)

        print("[GROUNDING RESULT]:")
        for result in grounding_results.output:
            print(result)
        print()


        print("[RUNNING SIMILARITY SCORING AGENT]")

        # filter out any grounded diseases that are missing a MONDO ID or phenotype
        filter_groundings = [
            d for d in grounding_results.output
            if d.mondo_id and d.phenotypes
        ]

        print("filter_groundings:", filter_groundings) # check filter_groundings

        # convert to required format as per computer_similarity_scoring function

        disease_hpo_map = {d.mondo_id: d.phenotypes for d in filter_groundings} # disease_hpo_map becomes a Dict[str, List[str]]→ MONDO ID → list of HPO terms
        disease_names = {d.mondo_id: d.disease_name for d in filter_groundings} #disease_names becomes a Dict[str, str]→ MONDO ID → readable disease name

        similarity_results = await compute_similarity_scores(
            patient_hpo_ids=hpo_ids,
            disease_hpo_map=disease_hpo_map,
            disease_names=disease_names)

        for result in similarity_results:
            print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    cli()
