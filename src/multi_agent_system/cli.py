import asyncio
import json
import time
import click
from pathlib import Path
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.agents.similarity_scoring.similarity_agent import similarity_agent

from multi_agent_system.utils.utils import extract_hpo_ids_and_sex


#  poetry run agents run_pipeline --phenopacket-dir multi_agent_system/phenopackets


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

        print(f"[INFO] Passing to input to breakdown agent: {breakdown_input}")
        print("[RUNNING BREAKDOWN AGENT]")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        await asyncio.sleep(0.5)

        print(f"[INFO] BREAKDOWN AGENT COMPLETE")
        print(f"[BREAKDOWN RESULT]:\n{breakdown_result}\n") # breakdown_result.output = InitialDiagnosisResult


        # GROUNDING AGENT
        # extract candidate disease name from InitialDiagnosisResult
        # breakdown_result.output is the InitialDiagnosisResult object

        print("[RUNNING GROUNDING AGENT]")
        candidate_disease_labels = [d.disease_name for d in breakdown_result.output.candidate_diseases]

        print("candidate_disease_labels:", candidate_disease_labels)
        print("Number of candidate disease:", len(candidate_disease_labels))

        grounding_results = await grounding_agent.run(candidate_disease_labels)
        await asyncio.sleep(0.5)

        print("[GROUNDING AGENT COMPLETE]:")
        # for result in grounding_results.output[0]:
        #     print(result)
        # print()

        print(" Number of output diseases after grounding:", len(grounding_results.output))

        # SIMILARITY AGENT

        print("[PRE-PROCESSING FOR SIMILARITY SCORING AGENT]")

        # all grounded diseases, even partially grounded one proceed to jaccard similarity scoring

        print("Filtered grounded results")
        filter_groundings = grounding_results.output

        # print("filter_groundings:", filter_groundings) # check filter_groundings

        candidate_diseases = [
            {
                "disease_name":d.disease_name,
                "mondo_id": d.mondo_id,
                "phenotypes": d.phenotypes,
                "cosine_score": d.cosine_score
            }

            for d in filter_groundings
        ]

        # print("Formatted candidate_diseases:", candidate_diseases [:1]) #debug the first item

        similarity_input = f"""

        Patient HPO IDs: {hpo_ids}
        Candidate Diseases: {
        json.dumps(candidate_diseases, indent=2)
        }
        "phenopacket_ids: {phenopacket_path.stem}
        """

        print(f"[INFO] Passed filtered grounded results as input to similarity scoring agent")
        # print(f"[INFO] Passing to similarity agent: {similarity_input}")

        print("[INFO] RUNNING SIMILARITY AGENT")
        similarity_results = await similarity_agent.run(similarity_input)
        await asyncio.sleep(1.5)

        # print(" Number of output diseases after grounding:", len(similarity_results.output))
        print("[INFO] SIMILARITY AGENT COMPLETE")
        # print(f"[SIMILARITY RESULT]:\n{similarity_results.output}\n")



if __name__ == "__main__":
    cli()
