import click
import asyncio
from pathlib import Path
from pheval.utils.file_utils import all_files
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent

#--------------------------------------------------
# RUN BREAKDOWN ONLY
#---------------------------------------------------
async def run_breakdown(phenopacket_dir: str):
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")

        # Extract HPO IDs and sex
        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        breakdown_input = f"""
        Patient case: {phenopacket_path.stem}
        HPO terms: {hpo_ids}
        Patient sex: {sex}

        Please provide initial diagnosis.
        """

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        response = await breakdown_agent.run(breakdown_input)
        print(response)

@click.group()
def cli():
    """Multi-agent diagnostic pipeline CLI"""
    pass

@cli.command(name="run_breakdown")
@click.option("--phenopacket-dir", type=click.Path(exists=True, file_okay=False), required=True)
def run_breakdown_only(phenopacket_dir: str):
    """Run only the Breakdown Agent on all phenopackets."""
    asyncio.run(run_breakdown(phenopacket_dir))


#-------------------------------------
# RUN GROUNDING AGENT
#------------------------------------










if __name__ == "__main__":
    cli()