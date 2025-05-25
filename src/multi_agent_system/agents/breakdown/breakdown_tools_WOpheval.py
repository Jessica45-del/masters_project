# Extract phenopacket without using pheval

import json
import os

def extract_phenopackets(directory):
    """
    Extracts HPO phenotype IDs from all phenopacket JSON files in the given directory.

    Args:
        directory (str): Path to the directory containing phenopacket JSON files.

    Returns:
        dict: A dictionary where keys are filenames and values are lists of HPO IDs.
    """
    phenotype_hpo_ids = {}

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                try:
                    data = json.load(f)
                    hpo_ids = [feature['type']['id'] for feature in data.get('phenotypicFeatures', [])]
                    phenotype_hpo_ids[filename] = hpo_ids
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing {filename}: {e}")

    return phenotype_hpo_ids

# Example usage:
# directory_path = "/mnt/data"
# results = extract_phenopackets(directory_path)
# print(results)
