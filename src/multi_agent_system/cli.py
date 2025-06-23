
#---------------------
#COMMAND TO RUN PIPELINE
# poetry run agents run_pipeline --phenopacket-dir multi_agent_system/phenopackets
# poetry run agents breakdown --run-evals
#----------------------

import json
import click
import asyncio
from pathlib import Path
from pheval.utils.file_utils import all_files
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.agents.similarity_scoring.similarity_agent import similarity_agent


# Placeholder imports for future agents
# from multi_agent_system.agents.aggregation.aggregator_agent import aggregator_agent


from multi_agent_system.agents.breakdown.breakdown_evals import create_eval_dataset



async def run_pipeline_async(phenopacket_dir: str):
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")

        # Extract HPO IDs and sex (PRE-PROCESSING STEP)
        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        # RUN BREAKDOWN AGENT (Agent 1)
        breakdown_input = {
            "hpo_ids": hpo_ids,
            "sex": sex,
            "name": phenopacket_path.stem
        }

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        await breakdown_agent.run(breakdown_input)

        # RUN GROUNDING AGENT (Agent 2)
        breakdown_result_path = Path("results/initial_diagnosis") / f"{phenopacket_path.stem}_initial_diagnosis.json"

        if not breakdown_result_path.exists():
            print(f"[ERROR] Missing breakdown output for {phenopacket_path.name}")
            continue

        grounding_result = await grounding_agent.run(str(breakdown_result_path))
        print(f"[GROUNDING RESULT] {phenopacket_path.stem}:\n{grounding_result.output}\n")

        # RUN SIMILARITY SCORE AGENT
        similarity_result = await similarity_agent.run({
            "patient_hpo_terms": hpo_ids,
            "candidate_diseases": json.loads(grounding_result.output)
        })
        print(f"[SIMILARITY RESULT] {phenopacket_path.stem}:\n{similarity_result.output}")

        # Step 5: (Optional) Aggregator Agent
        # await aggregator_agent.run(similarity_result)


#--------------------
# CLI Entry Point
#--------------------
@click.group()
def cli():
    """Multi-agent diagnostic pipeline CLI"""
    pass

# Full multi-agent pipeline
@cli.command(name="run_pipeline")
@click.option("--phenopacket-dir", type=click.Path(exists=True, file_okay=False), required=True)
def run_pipeline(phenopacket_dir: str):
    """Run the full multi-agent diagnostic pipeline (Agents 1 → 4)."""
    asyncio.run(run_pipeline_async(phenopacket_dir))


# ------------------------
# Evaluation
#---------------------------


@cli.command()
@click.option('--run-evals', is_flag=True, help="Run evaluation tests for the breakdown agent.")
def breakdown(run_evals):
    if run_evals:
        print("Running breakdown agent evaluations...")

        async def run_evals():
            dataset = create_eval_dataset()
            results = await dataset.evaluate(breakdown_agent.run)
            for result in results:
                print(result)

        asyncio.run(run_evals())

    # else:
    #     print("[INFO] Running breakdown agent normally...")
    #     # Default logic





if __name__ == "__main__":
    cli()





























