from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from app.config import settings
import logging

log = logging.getLogger(__name__)

def get_qdrant_client():
    if settings.qdrant_api_key:
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    else:
        client = QdrantClient(url=settings.qdrant_url)
    return client

def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int):
    existing = client.get_collections().collections
    names = [c.name for c in existing]
    if collection_name in names:
        log.info("Collection exists: %s", collection_name)
        return
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE)
    )
    log.info("Created collection %s with vector size %d", collection_name, vector_size)