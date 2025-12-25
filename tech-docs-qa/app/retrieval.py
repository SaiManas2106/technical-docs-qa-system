from qdrant_client import QdrantClient
from app.qdrant_client_wrapper import get_qdrant_client
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from app.config import settings
import numpy as np

model = SentenceTransformer(settings.embedding_model)

def hybrid_retrieve(question: str, collection: str, top_k: int=5, keyword_filters: dict | None=None):
    client = get_qdrant_client()
    q_emb = model.encode([question])[0].tolist()
    # basic vector search
    search_result = client.search(collection_name=collection, query_vector=q_emb, limit=top_k)
    # optionally apply keyword filters on payload
    results = []
    for r in search_result:
        payload = r.payload or {}
        text = payload.get('text', None)
        results.append({
            "id": r.id,
            "score": r.score,
            "payload": payload
        })
    # If keyword_filters are provided, prefer items that match payload keys
    if keyword_filters:
        filtered = []
        for item in results:
            payload = item['payload']
            ok = True
            for k, v in keyword_filters.items():
                pv = payload.get(k)
                if pv is None:
                    ok = False
                    break
                if isinstance(v, str) and v.lower() not in str(pv).lower():
                    ok = False
                    break
            if ok:
                filtered.append(item)
        # fall back to vector results if nothing matched
        if filtered:
            return filtered
    return results