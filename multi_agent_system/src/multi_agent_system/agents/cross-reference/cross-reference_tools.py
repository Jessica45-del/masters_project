"""
Measure similarity of the hpo id and phenotypes
"""


def calculate_jaccard_index(self, set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity index between two sets."""
    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return 0.0
    return intersection / union