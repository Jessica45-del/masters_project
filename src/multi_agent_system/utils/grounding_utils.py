import numpy as np
import faiss
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Define paths
BASE_DIR = Path(__file__).parent / "data"
INDEX_PATH = BASE_DIR / "mondo_faiss.index"
LABELS_PATH = BASE_DIR / "mondo_labels.json"
IDS_PATH = BASE_DIR / "mondo_ids.json"

# Load embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def load_faiss_index():
    """ Load faiss index """
    index = faiss.read_index(str(INDEX_PATH))
    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)
    with open(IDS_PATH, "r") as f:
        ids = json.load(f)
    return index, labels, ids

# Encode query (disease label) into a vector
def get_embedding(label: str) -> np.ndarray:
    prompt = f"search_query: {label}"
    embedding = model.encode([prompt])
    embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
    return embedding.astype("float32")

# Use cosine similarity to find most likely MONDO ID match
def cosine_similarity(label: str, k: int = 1, threshold: float = 0.60) -> dict:
    """ Similarity search using FAISS with cosine similarity

    Args:
        label (str): label (i.e. disease name) associated with the mondo
        k (int): number of nearest neighbors
        threshold (float): threshold of similarity

    Returns:
        A dictionary with the MONDO disease label and ID if the best match
        is above the threshold.
    """

    index, labels, ids = load_faiss_index()
    embedding = get_embedding(label)
    D, I = index.search(embedding, k)

    cosine_score = D[0][0]
    if cosine_score >= threshold and I[0][0] < len(labels): # check if cosine score above threshold + checks if FAISS index is valid
        match_label = labels[I[0][0]] # retrieve matched label (best matching MONDO disease name) from the labels list using FAISS index
        match_id = ids[I[0][0]] # retrieve the associated MONDO ID

        if isinstance(match_id, str) and match_id.startswith("MONDO:"):
            print(f"[Cosine Similarity Match] '{label}' → '{match_label}' ({match_id}) with score {cosine_score:.4f}")
            return {"label": match_label, "id": match_id, "cosine_score": float(cosine_score)}

        else:
            print(f"[Invalid Match ID] '{label}' matched '{match_label}' but returned non-MONDO ID: {match_id}")
            print(
                f"[No Valid MONDO Match] '{label}' scored {cosine_score:.4f}, but the best match ID was not a MONDO ID (got: {match_id})")


    elif cosine_score < threshold:
        # fallback if either cosine score is too low or ID is invalid
        print(f"[No Strong Match found] '{label}' scored {cosine_score:.4f}. No match above threshold {threshold}")

    return {
        "label": label,
        "id": "MONDO ID not found",

    }

#TEST

# if __name__ == "__main__":
#     test_label = "glutaric aciduria type 1"
#     print(f"Searching for MONDO ID for label: {test_label}")
#     result = cosine_similarity(test_label)
#
#     print("\nResult:")
#     print(result)