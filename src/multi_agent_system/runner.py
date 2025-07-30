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
from multi_agent_system.utils.batching_utils import calculate_batch_size
from multi_agent_system.utils.utils import extract_hpo_ids_and_sex

@dataclass
class AgentPhEvalRunner(PhEvalRunner):
    """Runner class implementation."""

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str

    def prepare(self):
        """Prepare."""
        print("preparing")

    def run(self):
        """Run Agent Pipeline through PhEval"""
        asyncio.run(self.run_pipeline_async())

    async def run_pipeline_async(self):
        """Async pipeline execution for PhEval runner"""
        phenopacket_dir = self.input_dir

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

            print("[RUNNING BREAKDOWN AGENT]")
            breakdown_result = await breakdown_agent.run(breakdown_input)
            print(f"Tokens used: {breakdown_result.usage().total_tokens}")
            await asyncio.sleep(0.5)

            # GROUNDING AGENT
            print("[RUNNING GROUNDING AGENT]")
            candidate_disease_labels = [d.disease_name for d in breakdown_result.output.candidate_diseases]

            grounding_batch_size = min(5, calculate_batch_size(
                candidate_disease_labels,
                max_tokens=3500,
                per_item_overhead=80
            ))

            grounding_results = []
            for i in range(0, len(candidate_disease_labels), grounding_batch_size):
                batch = candidate_disease_labels[i:i + grounding_batch_size]
                results = await grounding_agent.run(batch)
                grounding_results.extend(results.output)

            # SIMILARITY AGENT
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
                per_item_overhead=100
            ))

            all_similarity_results = []
            for i in range(0, len(candidate_diseases), similarity_batch_size):
                batch = candidate_diseases[i:i + similarity_batch_size]

                similarity_input = (
                    f"### PATIENT HPO TERMS ###\n"
                    f"{', '.join(hpo_ids)}\n\n"
                    f"### CANDIDATE DISEASES ###\n"
                    f"{json.dumps(batch, separators=(',', ':'), ensure_ascii=False)}\n\n"
                    f"### PHENOPACKET ID ###\n"
                    f"{phenopacket_path.stem}"
                )

                results = await similarity_agent.run(similarity_input)
                all_similarity_results.extend(results.output.results)
                await asyncio.sleep(0.5)

            sorted_results = sorted(
                all_similarity_results,
                key=lambda x: x.jaccard_similarity_score,
                reverse=True
            )[:10]  # Top 10 diseases

            # Save results in PhEval output format
            await save_agent_results(
                results=[
                    {
                        "disease_name": r.disease_name,
                        "mondo_id": r.mondo_id,
                        "score": r.jaccard_similarity_score
                    }
                    for r in sorted_results
                ],
                phenopacket_id=phenopacket_path.stem,
                output_dir=self.output_dir  # Use PhEval's output directory
            )

    def post_process(self):
        """Post Process."""
        print("post processing")