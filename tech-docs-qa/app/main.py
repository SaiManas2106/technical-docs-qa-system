from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.retrieval import hybrid_retrieve
from app.config import settings
import openai
import os

app = FastAPI(title="Tech Docs QA")

openai.api_key = settings.openai_api_key

class QueryRequest(BaseModel):
    question: str
    collection: Optional[str] = None
    top_k: Optional[int] = 5
    filters: Optional[dict] = None

@app.get('/health')
def health():
    return {"status":"ok"}

@app.post('/query')
async def query(req: QueryRequest):
    collection = req.collection or settings.qdrant_collection
    # retrieve context
    results = hybrid_retrieve(req.question, collection, top_k=req.top_k, keyword_filters=req.filters)
    context_texts = []
    for r in results:
        payload = r.get('payload', {})
        # payload might not contain original text in this simple ingestion, so try to open source file
        src = payload.get('source')
        chunk_index = payload.get('chunk_index')
        snippet = payload.get('snippet') or payload.get('text')
        if not snippet and src:
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    alltext = f.read()
                    # naive chunk read
                    tokens = alltext.split()
                    chunk_size = 500
                    overlap = 50
                    start = chunk_index * (chunk_size - overlap)
                    snippet = ' '.join(tokens[start:start+chunk_size])
            except Exception:
                snippet = ''
        context_texts.append(snippet)

    combined_context = "\n\n---\n\n".join([t for t in context_texts if t])

    if not combined_context:
        # if no context then don't hallucinate
        return {"answer": "I couldn't find relevant context in the indexed documents."}

    # Call OpenAI for final answer using retrieved context
    prompt = f"Context:\n{combined_context}\n\nQuestion:\n{req.question}\n\nAnswer concisely."
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # replace if necessary
            messages=[{"role":"system","content":"You are a helpful technical assistant."},
                      {"role":"user","content":prompt}],
            max_tokens=512,
            temperature=0.0,
        )
        answer = resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"answer": answer, "sources": [r.get('payload') for r in results]}