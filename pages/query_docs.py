
import lancedb
import streamlit as st

from app import ts
from config import (
    CLOUD_DB_URI,
    DEFAULT_FINAL_LLM_MODEL,
    DEFAULT_TEMPERATURE,
    MODEL_OPTIONS,
    N_RESULTS_RETRIEVED,
    N_TOP_RERANKED_RESULTS_TO_LLM,
    ldb_conn,
    rr_options,
)
from generate_llm_response import generate_response
from retrieval import get_most_relevant_chunks
from ui_element_long_strings import (
    NUM_RESULTS_RETRIEVED_HELP,
    NUM_RESULTS_TO_LLM_HELP,
    SELECTED_LLM_MODEL_HELP,
    SELECTED_RERANKER_HELP,
    TEMPERATURE_HELP,
)


def query_view():
    st.header("Query Mode")

    # Document Collection to Query
    db_tbl_names = list(ldb_conn.table_names())
    collection_names = [tn.split("_by_")[0] for tn in db_tbl_names]

    # SIDEBAR OPTIONS
    with st.sidebar:

        # Input Number of Chunks Retrieved by 1st Stage; range: 5-15
        num_results_retrieved = st.number_input(label="Number of Chunks Retrieved (1st Stage)",
                                                min_value=5, 
                                                max_value=15, 
                                                value=N_RESULTS_RETRIEVED,
                                                help=NUM_RESULTS_RETRIEVED_HELP)

        # Input Type of Reranker
        selected_reranker = st.selectbox(label="Type of Reranker",
                                         options=rr_options,
                                         index=0,
                                         help=SELECTED_RERANKER_HELP)

        # Input Number of Top-Reranked Chunks to LLM; range: 1-5
        num_results_to_llm = st.number_input(label="Number of Top-Reranked Chunks to LLM",
                                             min_value=1, 
                                             max_value=10, 
                                             value=N_TOP_RERANKED_RESULTS_TO_LLM,
                                             help=NUM_RESULTS_TO_LLM_HELP)

        selected_llm_model = st.selectbox(label="Final LLM Model",
                                          options=MODEL_OPTIONS, 
                                          index=MODEL_OPTIONS.index(DEFAULT_FINAL_LLM_MODEL),
                                          help=SELECTED_LLM_MODEL_HELP,
    )
        temperature = st.number_input(label="Temperature",
                                      min_value=0.0, max_value=1.0, value=DEFAULT_TEMPERATURE,
                                      help=TEMPERATURE_HELP)
    # MAIN (non-sidebar) VIEW
    collection = st.selectbox("Select a collection to query", options=collection_names, index=1)
    query = st.text_input("Enter your question or query")
    
    if query and collection:
        db_tblname = [tn for tn in db_tbl_names if tn.startswith(collection)][0]
        tbl = lancedb.connect(CLOUD_DB_URI).open_table(db_tblname)
        st.write(f"QUERY ({ts()}): '{query}'")
        retrieved_chunks = get_most_relevant_chunks(tbl, 
                                                    query, 
                                                    num_results_retrieved=num_results_retrieved,
                                                    num_results_to_llm=num_results_to_llm,
                                                    rr=selected_reranker,
                                                    )
        
        narrative_response = generate_response(query, 
                                            retrieved_chunks, 
                                            llm_name=selected_llm_model,
                                            temperature=temperature,
                                            )

        st.write(f"ANSWER ({ts()}): '{narrative_response}'")
        st.page_link(page='pages/view_source_doc.py', label='***view quote in source doc***', )

query_view()