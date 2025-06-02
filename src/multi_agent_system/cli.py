 """ Command line interface for Multi System Agents. """

import click
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider




model_option = click.option(
    "--model",
    "-m",
    help="The model to use for the agent.",
)

agent_option = click.option(
    "--agent",
    "-a",
    help="The agent to use (if non-default).",
)

server_port_option = click.option(
    "--server-port",
    "-p",
    default=7860,
    show_default=True,
    help="The port to run the UI server on.",
)



























#
# import click
# from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
# from multi_agent_system.agents.breakdown.breakdown_agent import extract_phenopacket_pipeline
#
# #  expand this dict when I add more agents
# AGENTS = {
#     "breakdown": breakdown_agent,
#     # "grounding": grounding_agent,
#     # "aggregate": aggregate_agent,
# }
#
# @click.group()
# def cli():
#     """Multi-Agent System CLI for Rare Disease Diagnosis"""
#     pass
#
#
# @cli.command()
# @click.option('--agent', type=click.Choice(AGENTS.keys()), required=True, help='Which agent to run')
# @click.option('--file', type=click.Path(exists=True), required=True, help='Path to phenopacket JSON file')
# def agent(agent, file):
#     """Run a specific agent on a single phenopacket file"""
#     agent_obj = AGENTS[agent]
#     result = agent_obj.run_sync(file)
#     click.echo("Output:")
#     click.echo(result.data)
#
#
# @cli.command()
# @click.option('--dir', 'dir_path', type=click.Path(exists=True, file_okay=False), required=True, help='Directory of phenopacket JSON files')
# def pipeline(dir_path):
#     """Run the full breakdown pipeline on a directory of phenopackets"""
#     click.echo(f" Running pipeline on directory: {dir_path}")
#     output_files = extract_phenopacket_pipeline(dir_path)
#     for path in output_files:
#         click.echo(f" Saved: {path}")
#
#
# if __name__ == "__main__":
#     cli()
