"""
retrieve.py - given a question, find the closest chunks in the vector database.
"""
import time

import chromadb
from openai import OpenAI

import config

_embed_client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)
_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        db = chromadb.PersistentClient(path=config.CHROMA_DIR)
        _collection = db.get_collection(config.COLLECTION_NAME)
    return _collection


def retrieve_chunks(query: str, top_k: int | None = None) -> dict:
    top_k = top_k or config.TOP_K
    started = time.time()

    response = _embed_client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=[config.QUERY_PREFIX + query],
    )
    result = _get_collection().query(
        query_embeddings=[response.data[0].embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        chunks.append({
            "content": text,
            "source": meta["source"],
            "page": meta["page"],
            "relevance_score": round(1 - distance, 4),  # cosine similarity
        })

    return {
        "query": query,
        "retrieved_chunks": chunks,
        "retrieval_time_ms": round((time.time() - started) * 1000),
        "embedding_model": config.EMBEDDING_MODEL,
    }


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "How many days of paid time off do employees get?"
    out = retrieve_chunks(q)
    print(f"{q}  ({out['retrieval_time_ms']} ms)")
    for c in out["retrieved_chunks"]:
        print(f"  {c['relevance_score']:.3f}  {c['source']} p.{c['page']}: {c['content'][:90]}...")
