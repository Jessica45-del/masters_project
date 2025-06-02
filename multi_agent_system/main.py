from pathlib import Path
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
# from multi_agent_system.agents.breakdown.breakdown_tools import extract_phenopackets
from multi_agent_system.agents.breakdown.breakdown_config import get_config

if __name__ == "__main__":
    phenopacket_dir = Path("multi_agent_system/phenopackets").resolve()

    result = breakdown_agent.run_sync(
        user_prompt=f"Please process phenopackets in directory: {phenopacket_dir}",
        deps=get_config()
    )

    print("HPO extraction complete.\n")
    print(result.output)
