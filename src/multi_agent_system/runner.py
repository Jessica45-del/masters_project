"""Runner."""

from dataclasses import dataclass
from pheval.runners.runner import PhEvalRunner
import asyncio
import json
from pathlib import Path
from pheval.utils.file_utils import all_files
from multi_agent_system.agents.breakdown.breakdown_agent import breakdown_agent
from multi_agent_system.agents.grounding.grounding_agent import grounding_agent
from multi_agent_system.agents.similarity_scoring.similarity_agent import similarity_agent
from multi_agent_system.agents.similarity_scoring.similarity_tools import save_agent_results
from multi_agent_system.post_process.post_process import post_process_format
from multi_agent_system.utils.batching_utils import calculate_batch_size
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex


@dataclass
class AgentPhEvalRunner(PhEvalRunner):
    """Runner class implementation."""

    input_dir: Path #paths to folder containing config
    testdata_dir: Path #phenopackets
    tmp_dir: Path
    output_dir: Path # paths to results dir
    config_file: Path
    version: str

    def prepare(self):
        """Prepare."""
        print("preparing")


    def run(self):
        """Run Agent Pipeline through PhEval"""
        print("[INFO] Starting pipeline...")
        asyncio.run(self._run_pipeline_async())



    async def _run_pipeline_async(self):
        """Full pipeline: Breakdown → Grounding → Similarity for all phenopackets"""
        print("[DEBUG] Entered _run_pipeline_async")
        phenopacket_dir = Path(self.testdata_dir)

        print(f"[DEBUG] Looking for files in: {phenopacket_dir}")
        print(f"[DEBUG] Directory exists: {phenopacket_dir.exists()}")

        for phenopacket_path in phenopacket_dir.glob("*.json"):
            print(f"\n[INFO] Processing: {phenopacket_path.name}")

            hpo_ids, sex = extract_hpo_ids_and_sex(phenopacket_path)

            # === BREAKDOWN AGENT ===
            breakdown_input = f"""
                   Patient case: {phenopacket_path.stem}
                   HPO terms: {hpo_ids}
                   Patient sex: {sex}
                   """
            print(f"[INFO] Passing to breakdown agent: {breakdown_input}")
            breakdown_result = await breakdown_agent.run(breakdown_input)
            print("Tokens used (if available):", breakdown_result.usage())
            await asyncio.sleep(0.5)
            print(f"[INFO] BREAKDOWN AGENT COMPLETE\n[RESULT]: {breakdown_result}\n")

            candidate_disease_labels = [
                d.disease_name for d in breakdown_result.output.candidate_diseases
            ]

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
            print("[GROUNDING AGENT COMPLETE]")

            candidate_diseases = [
                {
                    "disease_name": d.disease_name,
                    "mondo_id": d.mondo_id,
                    "phenotypes": list(d.phenotypes),
                    "cosine_score": d.cosine_score
                }

                for d in grounding_results
            ]

            similarity_batch_size = min(5, calculate_batch_size(
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


        print("PhEval Run step COMPLETE!")

    def post_process(self):
        """Post Process."""

        # post_process_format(
        #     agent_results=self.agent_results_dir,
        #
        # )
        print("post processing")