#!/usr/bin/env bash
python app/ingest.py --docs_dir examples/docs --collection tech_docs --model ${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}