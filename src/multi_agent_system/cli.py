from typing import List
# poetry run breakdown_agent --phenopacket-dir multi_agent_system/phenopackets
import click
import asyncio


from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
#from multi_agent_system.agents.breakdown.breakdown_tools import list_phenopacket_files


# Run breakdown agent -  currently running one directory at a time but want it to run by individual phenopacket at a time
async def run_breakdown_agent_async(phenopacket_dir: str):
    await breakdown_agent.run(phenopacket_dir)



@click.command()
@click.option("--phenopacket-dir", type=str)
def run_agent(phenopacket_dir:str):
    """Run the diagnostic agent pipeline on a folder of phenopacket files."""
    print(f"Received phenopacket_dir: {phenopacket_dir}")
   # for phenopacket_path in all_files(phenopacket_dir):
    asyncio.run(run_breakdown_agent_async(phenopacket_dir))

# # List phenopackets outside the agent
# async def run_breakdown_agent_async(phenopacket_dir: str):
#     file_paths = await list_phenopacket_files(phenopacket_dir)
#
# #Pass phenopackets to agent
#     for file_path in file_paths:
#         print(f"[INFO] Processing: {file_path}")
#         await breakdown_agent.run({"phenopacket_file": file_path})