import lancedb
import streamlit as st
import torch
from lancedb.embeddings import get_registry

# Constants
BUCKET_URL = "https://pub-ec8aa50844b34a22a2e6132f8251f8b5.r2.dev"
EMBEDDER = ("sentence-transformers", "BAAI/bge-small-en-v1.5")
TEXT_CLEANING_MODEL = "gemini/gemini-1.5-flash"
CLOUD_DB_URI = "db://askliz-doc-db-8qjgop" # "db://aireader9000-rlei9n"
CLOUD_DB_REGION = "us-east-1"
N_RESULTS_RETRIEVED = 5
N_TOP_RERANKED_RESULTS_TO_LLM = 3

# Load secrets
LANCEDB_API_KEY = st.secrets["LANCEDB_API_KEY"]
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]

# Load embedding model
nn_compute_hw = 'mps' if torch.backends.mps.is_available() else 'cpu'
embedding_model = get_registry().get(EMBEDDER[0]).create(name=EMBEDDER[1], device=nn_compute_hw)
#st.write(f"embedding_model.device = {embedding_model.device}")

# Doc DB connection  (lancedb cloud)
ldb_conn = lancedb.connect(CLOUD_DB_URI, api_key=LANCEDB_API_KEY, region=CLOUD_DB_REGION)

# Restricting model options now that we care more about structured output,
# which OpenAI supports in a particularly clean and reliable way.
# (pricing info below from https://openai.com/api/pricing/ as of 11/26/2024)
MODEL_OPTIONS = ['gpt-4o',                  # $2.50 / $10.00 price per M input/output tokens
                 'gpt-4o-2024-11-20',       # $2.50 / $10.00 
                 "gpt-4o-mini",             # $0.150 / $0.600
                 "gpt-4o-mini-2024-07-18"   # $0.150 / $0.600
                 "o1-mini",                 # $3.00 / $12.00 
                 ]

### USER CONFIGURABLE PARAMS ###
DEFAULT_FINAL_LLM_MODEL = "gpt-4o-mini"  # we should be able to get by w/ smallest model avaial here
DEFAULT_TEMPERATURE = 0.0  # 0.0 for more deterministic output, given I want direct
                           # quotes, and prioritization of higher-relevance-score passages

# Other sequences of options that otherwise spill to mult lines in app code
rr_options = ["CohereReranker", 
              "LinearCombinationReranker", 
              "CrossEncoderReranker", 
              "ColbertReranker"]
