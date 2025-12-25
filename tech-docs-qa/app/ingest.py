import os
import argparse
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from app.qdrant_client_wrapper import get_qdrant_client, ensure_collection
from app.nlp_pipeline import normalize_text, extract_entities
from typing import List, Dict
import uuid
import logging

log = logging.getLogger(__name__)

def read_text_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_text(text: str, chunk_size: int=500, overlap: int=50) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        chunks.append(' '.join(chunk))
        i += chunk_size - overlap
    return chunks

def build_points(docs: List[Dict], model_name: str):
    model = SentenceTransformer(model_name)
    texts = [d['text'] for d in docs]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    points = []
    for i, d in enumerate(docs):
        pid = d.get('id') or str(uuid.uuid4())
        points.append({
            "id": pid,
            "vector": embeddings[i].tolist(),
            "payload": d.get('meta', {})
        })
    return points, embeddings.shape[1]

def ingest_directory(docs_dir: str, collection: str, model_name: str):
    client = get_qdrant_client()
    # prepare docs
    docs = []
    for root, _, files in os.walk(docs_dir):
        for fn in files:
            if not fn.lower().endswith(('.txt','.md','.json','.rst')):
                continue
            path = os.path.join(root, fn)
            text = read_text_file(path)
            text = normalize_text(text)
            chunks = chunk_text(text)
            for j, c in enumerate(chunks):
                meta = {"source": path, "chunk_index": j, "original_len": len(c)}
                ents = extract_entities(c)
                if ents:
                    meta["entities"] = ents
                docs.append({"id": f"{os.path.basename(fn)}::{j}", "text": c, "meta": meta})
    if not docs:
        print("No documents found to ingest.")
        return
    points, vector_size = build_points(docs, model_name)
    ensure_collection(client, collection, vector_size)
    client.upsert(collection_name=collection, points=points)
    print(f"Ingested {len(points)} chunks into collection {collection}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--docs_dir', required=True, help='Directory containing docs to ingest')
    parser.add_argument('--collection', default='tech_docs', help='Qdrant collection name')
    parser.add_argument('--model', default='sentence-transformers/all-MiniLM-L6-v2', help='SentenceTransformer model')
    args = parser.parse_args()
    ingest_directory(args.docs_dir, args.collection, args.model)