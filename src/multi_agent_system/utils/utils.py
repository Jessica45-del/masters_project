# Utils for breakdown agent


SEX_MAP = {
    1: "Female",
    2: "Male",
    0: "Unknown",
}


from pathlib import Path
from typing import List, Tuple

from pheval.utils.phenopacket_utils import phenopacket_reader, PhenopacketUtil

#assign path outside the function


def extract_hpo_ids_and_sex(phenopacket_path: Path) -> Tuple[List[str], str]:
    """
    Extract HPO term IDs and patient sex from a phenopacket file.

    Args:
        phenopacket_path (Path): Path to the phenopacket file.

    Returns:
        Tuple[List[str], str]: A tuple containing a list of HPO IDs and the sex.
    """
    print(f"Reading phenopacket from: {phenopacket_path}")

    phenopacket = phenopacket_reader(phenopacket_path)
    print("Phenopacket loaded.")

    phenopacket_util = PhenopacketUtil(phenopacket)
    # print("PhenopacketUtil initialized.")

    observed_phenotypes = phenopacket_util.observed_phenotypic_features()
    # print(f"Observed phenotypes: {observed_phenotypes}")

    hpo_ids = [p.type.id for p in observed_phenotypes if p and p.type and p.type.id]
    # print(f"Extracted HPO IDs: {hpo_ids}")

    sex = phenopacket.subject.sex if phenopacket.subject and phenopacket.subject.sex else "UNKNOWN"
    print(f"Extracted sex: {sex}")

    sex_code = phenopacket.subject.sex if phenopacket.subject and phenopacket.subject.sex else 0
    sex = SEX_MAP.get(sex_code, "Unknown")
    print(f"Extracted sex: {sex}")

    return hpo_ids, sex
