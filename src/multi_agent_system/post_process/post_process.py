# Post process to generate parquet files for Pheval runner (tsv --> parquet)

from pathlib import Path
from pheval.post_processing.post_processing import generate_disease_result, SortOrder
from multi_agent_system.post_process.tsv_to_polars import tsv_to_polars


def post_process_format(raw_results: Path, output_dir: Path):
    """
    Transform agent results in tsv to polars dataframe and then parquet

    Args:
        raw_results: path to agent results
        output_dir: path to output directory containing final results in parquet format

    Returns:
        agent results in parquet format

    """
    polars_dfs = {}

    # Loop through all TSV files in the agent_results folder
    try:
        for agent_result in raw_results.glob("*.tsv"):
            df = tsv_to_polars(agent_result)
            polars_dfs[agent_result.stem] = df

        generate_disease_result(
            results=df,  # polars df
            sort_order=SortOrder.DESCENDING,  # sort ranking from highest to lowest
            output_dir=output_dir,  # save final df in pheval_gene_results
            result_path=results_path,  # path to original LLM json file
            phenopacket_dir=phenopacket_dir  # phenopackets directory
        )

    except ValueError as e:
        print(f"Error processing {results_file.name}: {e}")




    return polars_dfs

