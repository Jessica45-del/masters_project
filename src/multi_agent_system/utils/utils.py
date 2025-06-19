# Utils for breakdown agent

from pathlib import Path
from typing import List, Tuple

from pheval.utils.phenopacket_utils import phenopacket_reader, PhenopacketUtil


def extract_hpo_ids_and_sex(phenopacket_path: Path) -> Tuple[List[str], str]:
    """
    Extract HPO term IDs and patient sex from a phenopacket file.

    Args:
        phenopacket_path (Path): Path to the phenopacket file.

    Returns:
        Tuple[List[str], str]: A tuple containing a list of HPO IDs and the sex.
    """
    phenopacket = phenopacket_reader(phenopacket_path)
    phenopacket_util = PhenopacketUtil(phenopacket)

    observed_phenotypes = phenopacket_util.observed_phenotypic_features()

    hpo_ids = [p.type.id for p in observed_phenotypes if p and p.type and p.type.id] #extract HPO id

    sex = phenopacket.subject.sex if phenopacket.subject and phenopacket.subject.sex else "UNKNOWN" # extract m

    return hpo_ids, sex
