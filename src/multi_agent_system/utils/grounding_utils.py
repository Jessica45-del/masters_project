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
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_faiss_index():
    index = faiss.read_index(str(INDEX_PATH))
    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)
    with open(IDS_PATH, "r") as f:
        ids = json.load(f)
    return index, labels, ids

# Encode query (disease label) into a vector
def get_embedding(label: str) -> np.ndarray:
    embedding = model.encode([label])
    embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
    return embedding.astype("float32")

# Use cosine similarity to find most likely MONDO ID match
def search_mondo_fallback(label: str, k: int = 1) -> dict:
    index, labels, ids = load_faiss_index()
    embedding = get_embedding(label)
    D, I = index.search(embedding, k)

    if I[0][0] < len(labels):  # Check if match found
        match_label = labels[I[0][0]]
        match_id = ids[I[0][0]]
        print(f"[SIMILARITY MATCH] '{label}' → '{match_label}' ({match_id}) with score {D[0][0]:.4f}")
        return {"label": match_label, "id": match_id}

    print(f"NO similar match found for: {label}")
    return {"label": label, "id": None}
