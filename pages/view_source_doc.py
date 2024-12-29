def generate_pdf_viewer(html_template_file: str, pdf_url: str) -> str:
    with open(html_template_file, 'r') as file:
        template = file.read()
    
    # Replace the hardcoded URL with the dynamic one
    html_content = template.replace(
        "const pdfUrl = '<<<PDF_URL>>>';",
        f"const pdfUrl = '{pdf_url}';"
    )

    with open("pdf_viewer_final_output.html", 'w') as file:
        file.write(html_content)
    
    return html_content
