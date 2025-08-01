# Post process to generate parquet files for Pheval runner (tsv --> parquet)

from pathlib import Path
from pheval.post_processing.post_processing import generate_disease_result, SortOrder
# from multi_agent_system.post_process.tsv_to_polars import tsv_to_polars
import polars as pl
from pheval.utils.file_utils import all_files


def tsv_to_polars(agent_result_path: Path) -> pl.DataFrame:
    """ Convert agent results in tsv format to polar format and extract score and disease identifier

    Args:
        agent_result_path (Path): Path to the agent results file

    Returns:
        Polar DataFrame with score and disease identifier

    """
    try:
        # Read TSV file into a Polars DataFrame
        df = pl.read_csv(agent_result_path, separator="\t")

        # Check if required columns exist
        required_columns = {"score", "disease_identifier"}
        if not required_columns.issubset(set(df.columns)):
            raise ValueError(f"Missing one or more required columns: {required_columns}")

        # Select only the required columns
        return df.select(["score", "disease_identifier"])

    except Exception as e:
        # Return an error message inside a DataFrame
        return pl.DataFrame([{"error": "Could not parse TSV", "raw": str(e)}])



def post_process_format(raw_results_dir = Path, output_dir = Path, phenopacket_dir = Path) -> None:
    """
    Generate pheval results in parquet format from agent results in tsv format

    Args:
        raw_results_dir (Path): Path to the raw results directory
        output_dir (Path): Path to the output directory
        phenopacket_dir (Path): Path to the phenopacket directory

    """
    for result in all_files(raw_results_dir):
        pheval_agent_result = tsv_to_polars(result)
        generate_disease_result(
            results=pheval_agent_result,
            sort_order=SortOrder.DESCENDING,
            output_dir=output_dir,
            result_path=result,
            phenopacket_dir=phenopacket_dir,

        )





















# def post_process_format(raw_results_dir: Path, output_dir: Path, phenopacket_dir: Path):
#     """
#     Transform agent results in tsv to polars dataframe and then parquet
#
#     Args:
#         raw_results_dir: path to agent results
#         output_dir: path to output directory containing final results in parquet format
#
#     Returns:
#         agent results in parquet format
#
#     """
#     polars_dfs = {}
#
#     # Loop through all TSV files in the agent_results folder
#     try:
#         for agent_result_file in raw_results_dir.glob("*.tsv"):
#             df = tsv_to_polars(agent_result_file)
#             polars_dfs[agent_result_file.stem] = df
#
#
#         results_path = raw_results_dir / agent_result_file.name
#
#         generate_disease_result(
#             results=df,  # polars df
#             sort_order=SortOrder.ASCENDING,  # sort ranking from highest to lowest
#             output_dir=output_dir,  # save final df in pheval_gene_results
#             result_path=results_path,  # path to original LLM json file
#             phenopacket_dir=phenopacket_dir  # phenopackets directory
#         )
#
#     except ValueError as e:
#         print(f"Error processing {agent_result_file.name}: {e}")
#
#
#
#
#     return polars_dfs
#
