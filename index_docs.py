from datetime import datetime
from typing import Literal, Union
from zoneinfo import ZoneInfo

import pymupdf as fitz
import streamlit as st

from config import ldb_conn, ts
from schemas import DocumentChunk, DocumentChunkLanceRecord

def clean_name(model_name:str)->str:
    return model_name.replace('/', '_').replace('-', '_').replace('.', '_')

# pdf_document = fitz.open("FINAL_REPORT.pdf")
def index_doc_to_cloud_db(pdf_document:fitz.Document,
                          doc_title:str, 
                          embed_by:Literal["page_text", "page_image"] = "page_text",
                          chunk_strategy:Literal["whole_page"] = "whole_page",
                          embedding_model:str = "BAAI/bge-small-en-v1.5"
                          )->Union[str, None]:

        # Chunk up document by page (Each chunk must always map to a particular page number)
        chunks = []
        st.write(f"{ts()} Parsing/chunking document...")
        try:
            #for page in stqdm(list(pdf_document.pages())):
            for page in list(pdf_document.pages()):
                if embed_by == "page_text":
                    if chunk_strategy == "whole_page":
                        chunks.append(DocumentChunk(text=page.get_text(), 
                                                    doc_name=doc_title, 
                                                    pg_num_0idx=page.number))
                    else:
                        raise NotImplementedError(f"{chunk_strategy} chunk strat not implemented")
                else:
                    raise NotImplementedError("only 'page_text' embedding strategy is implemented")
        except Exception as e:
            st.error(f"{ts()} Error parsing/chunking document on page {page}: {e}")
            return None
        
        # Write chunks to cloud document db
        table_name = f"{clean_name(doc_title)}_by_{chunk_strategy}_{clean_name(embedding_model)}"
        if table_name in ldb_conn.table_names():
            ldb_conn.drop_table(table_name)

        st.write(f"{ts()} Writing doc chunks to db (involves generating vector embeddings)")
        tbl = ldb_conn.create_table(table_name, schema=DocumentChunkLanceRecord)
        tbl.add(chunks)
        tbl.create_fts_index("text", replace=True)
        
        return None
