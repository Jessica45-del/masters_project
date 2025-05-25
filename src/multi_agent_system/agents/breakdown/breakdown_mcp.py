# MCP Layer to interact externally


from mcp.server.fastmcp import FastMCP
from multi_agent_system.agents.breakdown.breakdown_agent import BREAKDOWN_SYSTEM_PROMPT, extract_phenopacket_pipeline


mcp = FastMCP("breakdown", instructions=BREAKDOWN_SYSTEM_PROMPT) #breakdown agent and breakdown system prompt

# Wrapper that receives JSON request

@mcp.tool()
async def extract_phenopacket(dir_path: str):
    # Directly call your sync orchestration tool
    return extract_phenopacket_pipeline(dir_path)

if __name__ == "__main__":
    mcp.run(transport="stdio") # serving layer