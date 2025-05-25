from pathlib import Path
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.breakdown.breakdown_tools import extract_phenopackets
from multi_agent_system.agents.breakdown.breakdown_config import get_config

if __name__ == "__main__":
    phenopacket_dir = Path("phenopackets").resolve()  # Adjust if needed

    result = breakdown_agent.run_sync(
        tool=extract_phenopackets,
        input="phenopeckets",
        deps=get_config()
    )

    print("HPO extraction complete.\n")
    print(result.data)
