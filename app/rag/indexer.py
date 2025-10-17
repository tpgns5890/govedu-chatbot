# Placeholder for document indexing (PDF/Doc/HTML → embeddings)
# Later: use langchain document loaders + Chroma vector store.
from pathlib import Path

def build_index(policies_dir: str, vector_dir: str):
    Path(vector_dir).mkdir(parents=True, exist_ok=True)
    # TODO: load docs, chunk, embed, persist to Chroma
    return {"ok": True, "indexed": 0}
