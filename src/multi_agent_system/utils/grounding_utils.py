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
def search_mondo_fallback(label: str, k: int = 1, threshold: float = 0.75) -> dict:
    """ Similarity search using FAISS with cosine similarity

    Args:
        label (str): label of the mondo
        k (int): number of nearest neighbors
        threshold (float): threshold of similarity

    Returns:
        A dictionary with the MONDO disease label and ID if the best match
        is above the threshold.
    """

    index, labels, ids = load_faiss_index()
    embedding = get_embedding(label)
    D, I = index.search(embedding, k)

    score = D[0][0]
    if score >= threshold and I[0][0] < len(labels):
        match_label = labels[I[0][0]]
        match_id = ids[I[0][0]]
        print(f"[Cosine Similarity Match] '{label}' → '{match_label}' ({match_id}) with score {score:.4f}")
        return {"label": match_label, "id": match_id}

    print(f"[No Strong Match found] '{label}' scored {score:.4f}. No match above threshold {threshold}")
    return {"label": label, "id": None}
