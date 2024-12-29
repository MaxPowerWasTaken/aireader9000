from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


def ts()->str:
    return datetime.now(tz=ZoneInfo('America/Chicago')).strftime('%I:%M:%S %p')

def main()->None:
    st.title("Welcome to AI Reader 9000")

    # Define pages (besides this homepage / entrypoint)
    upload_page = st.Page("pages/upload_docs.py", title="Upload Documents", icon="📄")
    query_page = st.Page("pages/query_docs.py", title = "Query Documents", icon = "🔍")
    view_source_page = st.Page("pages/view_source_doc.py",title="See Quote in Source Doc",icon="📄")

    pages = [upload_page, query_page, view_source_page]
    homepage = st.navigation(pages)

    homepage.run()

if __name__ == "__main__":
    main()