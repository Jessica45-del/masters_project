import click
import asyncio
from pathlib import Path
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.breakdown.breakdown_tools import(
list_phenopacket_files,
prepare_prompt,
extract_json_block,
save_breakdown_result,
)

async def run_agent_async(phenopacket_dir: str):
    files = await list_phenopacket_files(phenopacket_dir)

    for file in files:
        prompt, name = await prepare_prompt(file)
        response = await breakdown_agent.run(prompt)
        response_text = response.output
        result = await extract_json_block(response_text)
        await save_breakdown_result(result, name)



# async def run_agent_async(phenopacket_dir: str):
#     files = await list_phenopacket_files(phenopacket_dir)
#
#     for file in files:
#         print(f"Submitting to agent: {file}")
#         response = await breakdown_agent.run("", deps={"file_path": file})
#         result = await extract_json_block(response.output)
#         name = Path(file).stem
#         await save_breakdown_result(result, name)


@click.command()
@click.option("--phenopacket-dir", type=Path)
def run_agent(phenopacket_dir):
    """Run the diagnostic agent pipeline on a folder of phenopacket files."""
    print(f"Received phenopacket_dir: {phenopacket_dir}")
    asyncio.run(run_agent_async(phenopacket_dir))