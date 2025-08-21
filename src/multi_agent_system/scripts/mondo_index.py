# Utils for grounding agent
# If basic_search fails (or result is too ambiguous), fall back to vector search:
# Embed label
# Search FAISS index
# Return best match
# This file creates the mondo index, label
#must be updated to reflect mondo database updates

from oaklib import get_adapter
from oaklib.interfaces import BasicOntologyInterface
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

# define output directory for index files
output_dir = Path("../utils/data_2")
output_dir.mkdir(parents=True, exist_ok=True)


# embedding model
# for mac users remove trust_remote_code = True to run script
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True) #nomic

# load mondo db
adapter = get_adapter("sqlite:obo:mondo")

#retrieve MONDO entity IDs in MONDO ontology database
entities = list(adapter.entities())

# Filter and retrieve MONDO disease labels

mondo_labels = [] #i.e mondo terms
mondo_ids = []

#get primary label
for entity in entities:
    primary_label = adapter.label(entity)
    if primary_label:
        mondo_labels.append(primary_label)
        mondo_ids.append(entity)

# get synoymns

for syn in adapter.entity_aliases(entity) or []:
    if syn != primary_label:
        mondo_labels.append(syn)
        mondo_ids.append(entity)
# Produce embeddings for MONDO labels

embeddings = model.encode(mondo_labels, show_progress_bar=True)

# Normalise each vector
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# Convert embeddings to float32 - a requirement for FAISS
embeddings = embeddings.astype("float32")

# Create FAISS index and store vectors
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# Save index and metadata
    # Save FAISS index
faiss.write_index(index, str(output_dir / "mondo_faiss.index"))

# Save disease label and MONDO id to output_dir
with open(output_dir / "mondo_labels.json", "w") as f:
    json.dump(mondo_labels, f)

with open(output_dir / "mondo_ids.json", "w") as f:
    json.dump(mondo_ids, f)

