from pathlib import Path
# poetry run breakdown_agent --phenopacket-dir multi_agent_system/phenopackets
#from multi_agent_system.agents.breakdown.breakdown_tools import list_phenopacket_files
from typing import List
from pheval.utils.file_utils import all_files
import click
import asyncio
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent

###### ORIGINAL ######
#
# # Run breakdown agent -  currently running one directory at a time but want it to run by individual phenopacket at a time
# async def run_breakdown_agent_async(phenopacket_dir: str):
#     await breakdown_agent.run(phenopacket_dir)
#
#
# @click.command()
# @click.option("--phenopacket-dir", type=str)
# def run_agent(phenopacket_dir:str):
#     """Run the diagnostic agent pipeline on a folder of phenopacket files."""
#     print(f"Received phenopacket_dir: {phenopacket_dir}")
#     #for phenopacket_path in all_files(phenopacket_dir):
#     asyncio.run(run_breakdown_agent_async(phenopacket_dir))


# NEW BREAKDOWN/-CLI


import click
import asyncio
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent



async def run_breakdown_agent_async(phenopacket_dir: str):
    for phenopacket_path in all_files(Path(phenopacket_dir)):
        if not phenopacket_path.name.endswith(".json"):
            continue
        print(f"[INFO] Running agent on: {phenopacket_path.name}")
        await breakdown_agent.run(str(phenopacket_path))

@click.command()
@click.option("--phenopacket-dir", type=click.Path(exists=True, file_okay=False))
def run_agent(phenopacket_dir: str):
    print(f"Received phenopacket_dir: {phenopacket_dir}")
    asyncio.run(run_breakdown_agent_async(phenopacket_dir))


if __name__ == "__main__":
    run_agent()
