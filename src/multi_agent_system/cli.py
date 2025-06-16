from pathlib import Path
import click
import asyncio
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent

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

#-----------------------------------
# Grounding Agent Runner
#-----------------------------------

async def run_grounding_agent_async(results_dir: str):
    for json_file in Path(results_dir).glob("*.json"):
        print(f"[INFO] Running grounding agent on: {json_file.name}")
        await grounding_agent.run(str(json_file))

@click.command(name="grounding_agent")
@click.option("--results-dir", type=click.Path(exists=True, file_okay=False), required=True)
def run_grounding_agent(results_dir: str):
    print(f"Received results_dir: {results_dir}")
    asyncio.run(run_grounding_agent_async(results_dir))

@click.group()
def cli():
    pass

cli.add_command(run_agent)
cli.add_command(run_grounding_agent)

if __name__ == "__main__":
    cli()





#DO NOT DELETE
#if __name__ == "__main__":
  #  run_agent()
