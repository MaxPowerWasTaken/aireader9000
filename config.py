import lancedb
import streamlit as st
import torch

from sentence_transformers import SentenceTransformer
from lancedb.rerankers import CrossEncoderReranker
from lancedb.embeddings import get_registry

EMBEDDING_MODEL = ("sentence-transformers", "BAAI/bge-small-en-v1.5")
TEXT_CLEANING_MODEL = "gemini/gemini-1.5-flash"
CLOUD_DB_URI = "db://askliz-doc-db-8qjgop"
CLOUD_DB_REGION = "us-east-1"
CORPUS_PATH = "corpus/j6c_final_report/FINAL_REPORT.html"

# Load secrets
LANCEDB_API_KEY = st.secrets["LANCEDB_API_KEY"]

# Load embedding model
nn_compute_hw = 'mps' if torch.backends.mps.is_available() else 'cpu'
embedding_model = get_registry().get(EMBEDDING_MODEL[0]).create(name=EMBEDDING_MODEL[1], device=nn_compute_hw)
st.write(f"embedding_model.device = {embedding_model.device}")

# Doc DB connection  (lancedb cloud)
ldb_conn = lancedb.connect(CLOUD_DB_URI, api_key=LANCEDB_API_KEY, region=CLOUD_DB_REGION)