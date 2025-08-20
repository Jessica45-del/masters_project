# Post process to generate parquet files for Pheval runner (tsv --> parquet)

from pathlib import Path
from pheval.post_processing.post_processing import generate_disease_result, SortOrder
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
        return pl.DataFrame(schema={
            "score": pl.Float64,
            "disease_identifier": pl.Utf8,

        })

    except Exception as e:
        # Return an error message inside a DataFrame
        return pl.DataFrame(
            {
                "score": [],
                "disease_identifier":[],
            },
            schema={
                "score":pl.Float64,
                "disease_identifier":pl.Utf8,
            }
        )


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
            result_path=Path(str(result).replace("-agents", "")),
            phenopacket_dir=phenopacket_dir,

        )




