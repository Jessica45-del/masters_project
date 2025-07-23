import asyncio
import json
import time
import click
from pathlib import Path
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.agents.similarity_scoring.similarity_agent import similarity_agent
from multi_agent_system.agents.similarity_scoring.similarity_tools import save_agent_results
from multi_agent_system.utils.batching_utils import calculate_batch_size
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex


#  poetry run agents run_pipeline --phenopacket-dir multi_agent_system/phenopackets


@click.group()
def cli():
    """Multi-Agent System CLI for Rare Disease Diagnosis"""
    pass


@cli.command()
@click.option('--phenopacket-dir', type=click.Path(exists=True), required=True, help='Directory with phenopacket JSON files')
async def run_breakdown(phenopacket_dir: str):
    """Run only the breakdown agent (HPO → initial candidate diseases)"""
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")

        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        breakdown_input = f"""
        Patient case: {phenopacket_path.stem}
        HPO ids: {hpo_ids}
        Patient sex: {sex}

        Please provide initial diagnosis.
        """

        print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
        print("[RUNNING BREAKDOWN AGENT]")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        print(f"[BREAKDOWN RESULT]:\n{breakdown_result}\n")  # breakdown_result.output = InitialDiagnosisResult



@cli.command(name="run_pipeline")
@click.option('--phenopacket-dir', type=click.Path(exists=True), required=True, help='Directory with phenopacket JSON files')
def run_pipeline(phenopacket_dir: str):
    """Run full pipeline: Breakdown → Grounding → Similarity"""
    asyncio.run(run_pipeline_async(phenopacket_dir))

async def run_pipeline_async(phenopacket_dir: str):
    phenopacket_dir = Path(phenopacket_dir)

    for phenopacket_path in all_files(phenopacket_dir):
        if not phenopacket_path.name.endswith(".json"):
            continue

        print(f"\n[INFO] Processing: {phenopacket_path.name}")
        hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

        # BREAKDOWN AGENT
        breakdown_input = f"""
        Patient case: {phenopacket_path.stem}
        HPO terms: {hpo_ids}
        Patient sex: {sex}
    
        """

        print(f"[INFO] Passing to input to breakdown agent: {breakdown_input}")
        print("[RUNNING BREAKDOWN AGENT]")
        breakdown_result = await breakdown_agent.run(breakdown_input)
        print("Tokens used (if available):", breakdown_result.usage())
        await asyncio.sleep(0.5)

        print(f"[INFO] BREAKDOWN AGENT COMPLETE")
        print(f"[BREAKDOWN RESULT]:\n{breakdown_result}\n") # breakdown_result.output = InitialDiagnosisResult


        # GROUNDING AGENT
        # extract candidate disease name from InitialDiagnosisResult
        # breakdown_result.output is the InitialDiagnosisResult object

        print("[RUNNING GROUNDING AGENT]")
        candidate_disease_labels = [d.disease_name for d in breakdown_result.output.candidate_diseases]

        # calculate batch size


        grounding_batch_size = min(5, calculate_batch_size(
            candidate_disease_labels,
            max_tokens=3500,  # Leave room for response
            per_item_overhead=80  # Account for agent prompt overhead
        ))
        print(f"Grounding batch size: {grounding_batch_size}, Total items: {len(candidate_disease_labels)}")

        # Process in dynamically sized batches
        grounding_results = []
        for i in range(0, len(candidate_disease_labels), grounding_batch_size):
            batch = candidate_disease_labels[i:i + grounding_batch_size]
            print(f"Processing grounding batch {i // grounding_batch_size + 1} with {len(batch)} items")
            results = await grounding_agent.run(batch)
            print(f"Tokens used: {results.usage().total_tokens}")
            grounding_results.extend(results.output)


        print("[INFO] Number of grounded diseases", len(grounding_results))








        # print("candidate_disease_labels:", candidate_disease_labels)
        # print("Number of candidate disease:", len(candidate_disease_labels))
        #
        # grounding_results = await grounding_agent.run(candidate_disease_labels)
        # print("Tokens used (if available):", grounding_results.usage())
        # await asyncio.sleep(0.5)

        print("[GROUNDING AGENT COMPLETE]:")
        # for result in grounding_results.output[0]:
        #     print(result)
        # print()

        # print(" Number of output diseases after grounding:", len(results.output))
        #
        # # SIMILARITY AGENT
        #
        # print("[PRE-PROCESSING FOR SIMILARITY SCORING AGENT]")
        #
        # # all grounded diseases, even partially grounded one proceed to jaccard similarity scoring
        #
        # print("Filtered grounded results")
        # filter_groundings = grounding_results
        #
        # print("filter_groundings:", filter_groundings) # check filter_groundings

        candidate_diseases = [
            {
                "disease_name":d.disease_name,
                "mondo_id": d.mondo_id,
                "phenotypes": list(d.phenotypes),
                "cosine_score": d.cosine_score
            }

            for d in grounding_results
        ]

        # print("Formatted candidate_diseases:", candidate_diseases [:1]) #debug the first item

        # Calculate safe batch size for similarity agent
        similarity_batch_size = min(5,calculate_batch_size(
            candidate_diseases,
            max_tokens=3500,
            per_item_overhead=100  # Higher overhead due to phenotype data
        ))
        print(f"Similarity batch size: {similarity_batch_size}, Total items: {len(candidate_diseases)}")

        # Process in batches
        all_similarity_results = []
        for i in range(0, len(candidate_diseases), similarity_batch_size):
            batch = candidate_diseases[i:i + similarity_batch_size]
            print(f"Processing similarity batch {i // similarity_batch_size + 1} with {len(batch)} items")

            similarity_input = (
                f"### PATIENT HPO TERMS ###\n"
                f"{', '.join(hpo_ids)}\n\n"
                f"### CANDIDATE DISEASES ###\n"
                f"{json.dumps(batch, separators=(',', ':'), ensure_ascii=False)}\n\n"
                f"### PHENOPACKET ID ###\n"
                f"{phenopacket_path.stem}"
            )

            print("[DEBUG] Prompt length (chars):", len(similarity_input))
            print("[DEBUG] Estimated tokens:", len(similarity_input) // 4)

            results = await similarity_agent.run(similarity_input)
            all_similarity_results.extend(results.output.results)
            print(f"Tokens used: {results.usage().total_tokens}")
            await asyncio.sleep(0.5)

        # print(f"[SIMILARITY RESULT]:\n{all_similarity_results}\n")
        sorted_results = sorted(
            all_similarity_results,
            key=lambda x: x.jaccard_similarity_score,
            reverse=True
        )[:10]  # Top 10 diseases

        print(f"[SIMILARITY RESULT - TOP 10]:\n{sorted_results}\n")

        print("[INFO] SIMILARITY AGENT COMPLETE")

        # convert similarity agent output which is an object into a dictionary
        await save_agent_results(
            results=[
                {
                    "disease_name": r.disease_name,
                    "mondo_id": r.mondo_id,
                    "score": r.jaccard_similarity_score
                }
                for r in sorted_results
            ],
            phenopacket_id=phenopacket_path.stem
        )


        #
        # similarity_input = f"""
        #
        # Patient HPO IDs: {hpo_ids}
        # Candidate Diseases: {
        # json.dumps(candidate_diseases, indent=2)
        # }
        # "phenopacket_ids: {phenopacket_path.stem}
        # """
        #
        # print(f"[INFO] Passed filtered grounded results as input to similarity scoring agent")
        # # print(f"[INFO] Passing to similarity agent: {similarity_input}")
        #
        # print("[INFO] RUNNING SIMILARITY AGENT")
        # similarity_results = await similarity_agent.run(similarity_input)
        # print("Tokens used (if available):", similarity_results.usage())
        # await asyncio.sleep(1.5)
        #
        # # print("Number of output diseases after grounding:", len(similarity_results.output))
        # print("[INFO] SIMILARITY AGENT COMPLETE")
        # # print(f"[SIMILARITY RESULT]:\n{similarity_results.output}\n")



if __name__ == "__main__":
    cli()
