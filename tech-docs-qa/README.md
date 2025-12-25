# Technical Documentation Q&A System (Knowledge Extraction)

**Duration:** Jun 2025 – Sep 2025  
**Stack:** Python, LangChain, OpenAI API, Qdrant, FastAPI, Sentence Transformers

## Overview
This repository implements a Technical Documentation Q&A system that:
- Extracts structured engineering information from heterogeneous technical specs.
- Applies semantic normalization and entity extraction for component hierarchies.
- Stores dense embeddings in Qdrant and supports hybrid retrieval (vector + keyword).
- Serves a FastAPI endpoint to answer user questions using OpenAI and retrieved context.
- Provides an evaluation framework to measure accuracy, precision, and response consistency.

## Features
- Document ingestion pipeline (chunking, embedding, upsert to Qdrant).
- Custom (rule-based + spaCy optional) entity extractor for component hierarchies and dependencies.
- Semantic normalization utilities (synonym mapping, basic canonicalization).
- Hybrid retriever combining vector similarity with payload keyword filtering.
- Prompt templates and simple prompt engineering iterators.
- Evaluation utilities to measure QA performance.

## Setup (local)
1. Clone this repo (or extract the zip).
2. Create virtualenv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   _Note: If you don't want `spacy`, skip installing that extra._

3. Run Qdrant (Docker recommended):
   ```bash
   docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
   ```

4. Copy `.env.example` -> `.env` and fill your `OPENAI_API_KEY` and (optionally) `QDRANT_URL`.

5. Ingest example documents:
   ```bash
   python app/ingest.py --docs_dir examples/docs --collection tech_docs
   ```

6. Run the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. Query the API:
   ```bash
   python examples/sample_query.py --question "What are the main power requirements of component X?"
   ```

## Project Structure
- `app/` - application code (ingest, retrieval, qdrant wrapper, pipeline, evaluation).
- `examples/` - sample docs and query script.
- `tests/` - basic unit tests for ingestion/retrieval.
- `requirements.txt` - Python dependencies.
- `Dockerfile` - optional containerization for the FastAPI app.

## Deployment
- Dockerize the FastAPI app (Dockerfile provided).
- Ensure Qdrant is accessible (hosted or self-managed).
- Use environment variables to configure keys and model choices.

## Notes & TODOs
- This is a reference implementation. For production: secure API keys, run Qdrant in HA mode, add batching and async ingestion, and include monitoring/logging.
- Replace `langchain` placeholder version with a concrete version compatible with your environment.

## License
MIT