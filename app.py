import pymupdf as fitz
import streamlit as st

from datetime import datetime
from zoneinfo import ZoneInfo

from index_docs import index_doc_to_cloud_db

# timestamping util function
def ts()->str:
    return datetime.now(tz=ZoneInfo('America/Chicago')).strftime('%I:%M:%S %p')

def main()->None:
    st.title("Welcome to AI Reader 9000")
    
    uploaded_file = st.file_uploader("Upload Document", type="pdf")
    if uploaded_file is not None:
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            doc_name = st.text_input("Enter a name for this document:")
            # proceed after doc_name is set
            if doc_name:
                index_doc_to_cloud_db(pdf_document, doc_title=doc_name)
                st.write(f"{ts()} Successfully indexed document: {doc_name}")

        except Exception as e:
            st.error(e)


if __name__ == "__main__":
    main()