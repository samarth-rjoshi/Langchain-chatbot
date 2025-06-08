from fpdf import FPDF
import os

def convert_txt_to_pdf(txt_folder, pdf_folder):
    # Ensure the output PDF folder exists
    os.makedirs(pdf_folder, exist_ok=True)

    # Get a list of all text files in the txt_folder
    txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]

    # Convert each text file to PDF
    for txt_file in txt_files:
        # Open the text file and read its content
        with open(os.path.join(txt_folder, txt_file), 'r', encoding='utf-8') as file:
            text_content = file.read()

        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()

        # Add a font
        pdf.set_font("Arial", size=12)

        # Add the text content to the PDF
        pdf.multi_cell(0, 10, text_content.encode('latin-1', 'replace').decode('latin-1'))

        # Save the PDF to the pdf_folder
        pdf_output_path = os.path.join(pdf_folder, os.path.splitext(txt_file)[0] + '.pdf')
        pdf.output(pdf_output_path)

# Define the paths to the folders
txt_folder_path = "data\LangChain Expression Language"
pdf_folder_path = "data\LangChain Expression Language/pdf_files"

# Convert text files to PDFs
convert_txt_to_pdf(txt_folder_path, pdf_folder_path)
