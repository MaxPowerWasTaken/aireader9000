
import pymupdf as fitz
import streamlit as st

from config import BUCKET_URL
from home import ts
from index_docs import index_doc_to_cloud_db
from ui_element_long_strings import COLLECTION_HELP


def upload_pdf_to_bucket(uploaded_file, BUCKET_URL, collection, doc_name):
    # upload uploaded_file to R2 location at: BUCKET_URL/collection/doc_name
    pass

def upload_view():
    uploaded_file = st.file_uploader("Upload a Document to Query", type="pdf")
    if uploaded_file is not None:
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            doc_name = st.text_input("Enter a name for this document:")
            collection = st.text_input("Enter a name for the collection this document goes in",
                                    help=COLLECTION_HELP,
                                    value=doc_name)

            if st.button("Process Document"):
                if not doc_name or not collection:
                    st.error("Please enter a name for the document and the collection it goes in.")

                upload_pdf_to_bucket(uploaded_file, BUCKET_URL, collection, doc_name)
                index_doc_to_cloud_db(pdf_document, doc_title=doc_name)
                st.write(f"{ts()} Successfully indexed document: {doc_name}")

        except Exception as e:
            st.error(e)

#st.set_page_config(page_title="Upload Document(s)", page_icon="⬆️")
#st.sidebar.header("Upload Document(s)")
st.header("Upload Mode")
upload_view()