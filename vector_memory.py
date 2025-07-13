"""
Very small wrapper around ChromaDB + sentence-transformers.
• add(text)              – store one doc
• query(text, k=3)       – [(score, doc), …]   lower score ≈ better
"""

from __future__ import annotations
from pathlib import Path
from uuid import uuid4

import chromadb
from sentence_transformers import SentenceTransformer


class VectorMemory:
    def __init__(self, persist_dir: str = ".vector_store"):
        self.store = Path(persist_dir)
        self.store.mkdir(exist_ok=True)

        # persistent Chroma client
        self.client = chromadb.PersistentClient(path=str(self.store))
        self.col = self.client.get_or_create_collection("mem")

        # one-liner embedder (MiniLM ≈ 80 MB)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # ---- API ----------------------------------------------------
    def add(self, doc: str) -> None:
        emb = self.embedder.encode([doc]).tolist()
        self.col.add(ids=[str(uuid4())], documents=[doc], embeddings=emb)

    def query(self, query: str, top_k: int = 3):
        emb = self.embedder.encode([query]).tolist()
        res = self.col.query(query_embeddings=emb, n_results=top_k)
        dists = res["distances"][0]
        docs  = res["documents"][0]
        return list(zip(dists, docs))
