"""
MCP tools for Breakdown Agent
"""
from pathlib import Path
from typing import Tuple, List

from mcp.server.fastmcp import FastMCP
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex
from multi_agent_system.agents.breakdown.breakdown_agent import BREAKDOWN_SYSTEM_PROMPT
from multi_agent_system.agents.breakdown.breakdown_tools import (

   prepare_prompt,
   extract_json_block,
   save_breakdown_result,
)

mcp = FastMCP("breakdown", instructions=BREAKDOWN_SYSTEM_PROMPT) #breakdown agent and breakdown system prompt



@mcp.tool()
async def construct_diagnosis_prompt(hpo_ids: List[str], sex: str) -> str:
    """
    Prepare prompt

    Args:
        hpo_ids: List of hpo ids
        sex: Patient sex

    Returns:

    """
    prompt = await prepare_prompt(hpo_ids, sex)
    return prompt

@mcp.tool()
async def get_json_block(text:str) -> list[dict]:
   """
   Extract JSON block from text and return it as a list.

   Args:
       text: JSON text block from deepseek model output

   Returns:
       JSON block from deepseek model
   """
   return await extract_json_block(text)


@mcp.tool()
async def save_results(data:list[dict], name: str) -> Path:
   """
   Save results in JSON file to initial_diagnosis directory located in the results directory

   Args:
       data: The response from deepseek in JSON format
       name: The name of phenopacket file

   Returns:
      A JSON output file with the patient HPO IDs, phenotype (label), systems affects
      and initial diagnosis
   """
   return await save_breakdown_result(data, name)


print("Starting breakdown MCP script...")


if __name__ == "__main__":
   # initialise and run the server
   mcp.run(transport="stdio") # serving layer



