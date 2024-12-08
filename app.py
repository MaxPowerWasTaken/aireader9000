import pymupdf as fitz
import streamlit as st


def main():
    st.title("Welcome to AI Reader 9000")
    
    uploaded_file = st.file_uploader("Upload Document", type="pdf")
    
    if uploaded_file is not None:
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            num_pages = len(pdf_document)
            st.write(f"Number of pages in the PDF: {num_pages}")
            pdf_document.close()
        except Exception:
            st.error("Error processing the PDF file")


if __name__ == "__main__":
    main()