
from pathlib import Path
import click
import asyncio

from pheval.utils.file_utils import all_files
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent

# Placeholder imports for future agents
# from multi_agent_system.agents.similarity.similarity_agent import similarity_agent
# from multi_agent_system.agents.aggregation.aggregator_agent import aggregator_agent


# poetry run agents run_pipeline --phenopacket-dir multi_agent_system/phenopackets


async def run_pipeline_async(phenopacket_dir: str):
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")

        # Step 1: Extract HPO IDs and sex
        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        # Step 2: Run Breakdown Agent (Agent 1)
        breakdown_input = {
            "hpo_ids": hpo_ids,
            "sex": sex,
            "name": phenopacket_path.stem  # Keep original patient ID (as you want)
        }

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        await breakdown_agent.run(breakdown_input)

        # Step 3: Run Grounding Agent (Agent 2)
        breakdown_result_path = Path("results/initial_diagnosis") / f"{phenopacket_path.stem}_initial_diagnosis.json"

        if not breakdown_result_path.exists():
            print(f"[ERROR] Missing breakdown output for {phenopacket_path.name}")
            continue

        grounding_result = await grounding_agent.run(str(breakdown_result_path))
        print(f"[GROUNDING RESULT] {phenopacket_path.stem}:\n{grounding_result.output}\n")

        # Step 4: (Optional) Similarity Agent
        # similarity_result = await similarity_agent.run(grounding_result)

        # Step 5: (Optional) Aggregator Agent
        # await aggregator_agent.run(similarity_result)

@click.command(name="run_pipeline")
@click.option("--phenopacket-dir", type=click.Path(exists=True, file_okay=False), required=True)
def run_pipeline(phenopacket_dir: str):
    """Run the full multi-agent diagnostic pipeline (Agents 1 → 4)."""
    asyncio.run(run_pipeline_async(phenopacket_dir))


@click.group()
def cli():
    pass


cli.add_command(run_pipeline)

if __name__ == "__main__":
    cli()
































