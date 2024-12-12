# this file is to help avoid adding extra code lines to ui components in app.py
# in order to just label or describe (via help/hover text) things clearly

# UPLOAD VIEW
COLLECTION_HELP = """In the Query view, we can query collections of documents. Defaults to name 
of doc, but you can rename if you want to add multiple docs to a single collection."""

# QUERY VIEW
NUM_RESULTS_RETRIEVED_HELP = """Number of document chunks retrieved from the document database
 (1st stage; before re-ranking)"""

SELECTED_RERANKER_HELP = """Type of reranker to use ranking (and implicitly, filtering) which 
retrieved document chunks are passed as context to the final LLM model for a final answer"""

NUM_RESULTS_TO_LLM_HELP = """Number of document chunks passed as context to the final LLM model 
for a final answer"""

SELECTED_LLM_MODEL_HELP = """LLM Model which takes the most-relevant retrieved document chunks, and 
formulates a final answer"""

TEMPERATURE_HELP = """Temperature parameter for LLM model (lower value for more deterministic)"""