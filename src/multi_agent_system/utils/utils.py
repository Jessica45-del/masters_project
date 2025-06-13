
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

    hpo_ids = [p.type.id for p in phenopacket_util.observed_phenotypic_features()] #extract HPO id
    sex = phenopacket.subject.sex if phenopacket.subject and phenopacket.subject.sex else "UNKNOWN" # extract m

    return hpo_ids, sex



# from pathlib import Path
# from typing import List
#
# from pheval.utils.phenopacket_utils import phenopacket_reader, PhenopacketUtil

#
# def extract_hpo_ids(phenopacket_path: Path) -> List[str]:
#     # Load phenopacket as an object
#     phenopacket = phenopacket_reader(Path(phenopacket_path))
#     hpo_ids = [p.type.id for p in PhenopacketUtil(phenopacket).observed_phenotypic_features()]
#
#     # Extract patient metadata
#     sex = phenopacket.subject.sex if phenopacket.subject and phenopacket.subject.sex else "UNKNOWN"
#
#     # Extract HPO term IDs
#     return [p.type.id for p in PhenopacketUtil(phenopacket).observed_phenotypic_features()]
