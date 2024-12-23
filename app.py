from datetime import datetime
from zoneinfo import ZoneInfo

import lancedb
import pymupdf as fitz
import streamlit as st

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
from index_docs import index_doc_to_cloud_db
from retrieval import get_most_relevant_chunks
from ui_element_long_strings import (
    COLLECTION_HELP,
    NUM_RESULTS_RETRIEVED_HELP,
    NUM_RESULTS_TO_LLM_HELP,
    SELECTED_LLM_MODEL_HELP,
    SELECTED_RERANKER_HELP,
    TEMPERATURE_HELP,
)


def ts()->str:
    return datetime.now(tz=ZoneInfo('America/Chicago')).strftime('%I:%M:%S %p')

def upload_view():
    st.header("Upload Mode")
    uploaded_file = st.file_uploader("Upload a Document to Query", type="pdf")
    if uploaded_file is not None:
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            doc_name = st.text_input("Enter a name for this document:")
            collection = st.text_input("Enter a name for the collection this document goes in",
                                       help=COLLECTION_HELP,
                                       value=doc_name)

            # Process the doc once user enters a doc- and collection-name, and hits button
            if st.button("Process Document"):
                if not doc_name or not collection:
                    st.error("Please enter a name for the document and the collection it goes in.")

                index_doc_to_cloud_db(pdf_document, doc_title=doc_name)
                st.write(f"{ts()} Successfully indexed document: {doc_name}")

        except Exception as e:
            st.error(e)


def query_view():
    st.header("Query Mode")

    # SIDEBAR OPTIONS
    with st.sidebar:
        # Document Collection to Query
        db_tbl_names = list(ldb_conn.table_names())
        collection_names = [tn.split("_by_")[0] for tn in db_tbl_names]
        collection = st.selectbox("Select a collection to query", options=collection_names)
        db_tbl = [tn for tn in db_tbl_names if tn.startswith(collection)][0]

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
    query = st.text_input("Enter your question or query")
    
    if query:
        #tbl = lancedb.connect(CLOUD_DB_URI, api_key=LANCEDB_API_KEY).open_table("document_chunks")
        tbl = lancedb.connect(CLOUD_DB_URI).open_table(db_tbl)
        st.write(f"type(tbl): {type(tbl)}")
        st.write(f"QUERY ({ts()}): '{query}'")
        retrieved_chunks = get_most_relevant_chunks(tbl, 
                                                    query, 
                                                    num_results_retrieved=num_results_retrieved,
                                                    num_results_to_llm=num_results_to_llm,
                                                    rr=selected_reranker,
                                                    )
        
        final_response, _ = generate_response(query, 
                                            retrieved_chunks, 
                                            llm_name=selected_llm_model,
                                            temperature=temperature,
                                            )
        st.write(f"ANSWER ({ts()}):\n{final_response}")

def main()->None:
    st.title("Welcome to AI Reader 9000")
    
    # Create tabs for main mode selection
    tab1, tab2 = st.tabs(["📄 Upload Documents", "🔍 Query Documents"])
    
    with tab1:
        upload_view()
    
    with tab2:
        query_view()

if __name__ == "__main__":
    main()