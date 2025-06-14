from pathlib import Path
import click
import asyncio
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent


async def run_breakdown_agent_async(phenopacket_dir: str):
    for phenopacket_path in all_files(Path(phenopacket_dir)):
        if not phenopacket_path.name.endswith(".json"):
            continue
        print(f"[INFO] Running breakdown agent on: {phenopacket_path.name}")
        await breakdown_agent.run(str(phenopacket_path))

@click.command()
@click.option("--phenopacket-dir", type=click.Path(exists=True, file_okay=False))
def run_agent(phenopacket_dir: str):
    print(f"Received phenopacket_dir: {phenopacket_dir}")
    asyncio.run(run_breakdown_agent_async(phenopacket_dir))


if __name__ == "__main__":
    run_agent()
