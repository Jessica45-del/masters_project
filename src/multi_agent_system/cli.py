""" Command line interface for Diagnostic Reasoning Agents."""

import click
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.breakdown.breakdown_config import get_config

# You can add more agents here later
AGENTS = {
    "breakdown": breakdown_agent,
    # "grounding": grounding_agent,
    # "aggregate": aggregate_agent,
}

@click.group()
def cli():
    """Multi-Agent System CLI for Rare Disease Diagnosis"""
    pass

@cli.command()
@click.option('--agent', type=click.Choice(AGENTS.keys()), required=True, help='Which agent to run')
@click.option('--file', type=click.Path(exists=True), required=True, help='Path to phenopacket JSON file')
def agent(agent, file):
    """Run a specific agent with a given input file"""
    agent_obj = AGENTS[agent]
    result = agent_obj.run_sync(file, deps=get_config())
    click.echo("Output:")
    click.echo(result.data)

if __name__ == "__main__":
    cli()
