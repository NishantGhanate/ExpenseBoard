"""
Docstring for app.pdf_normalizer.pdf_unlock

> python app/pdf_normalizer/pdf_unlock.py files/XXXXXXXX.pdf -p XXXXX

> python app/pdf_normalizer/pdf_unlock.py files/XXXX-XXXXXXX.pdf -p XXXXX

> python app/pdf_normalizer/pdf_unlock.py files/union1.pdf -p XXXXXXXX
"""


import argparse
import logging
from io import BytesIO

import pdfplumber
import pikepdf

logger = logging.getLogger(name="app")



def is_pdf_password_protected_bytes(pdf_bytes: bytes) -> bool:
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            _ = pdf.pages[0]
        return False
    except Exception as e:
        return "password" in str(e).lower()

def is_pdf_password_protected(file_path: str) -> bool:
    try:
        with pdfplumber.open(file_path) as pdf:
            _ = pdf.pages[0]  # try accessing first page
        return False
    except Exception as e:
        # Typical error: "Password required or incorrect password"
        return "password" in str(e).lower()


def unlock_pdf(file_path: str, password: str):

    # Unlock PDF
    output_path = file_path or file_path.replace(".pdf", "_unlocked.pdf")
    with pikepdf.open(file_path, password=password) as pdf:
        pdf.save(output_path)
        logger.info(f"Unlocked PDF saved to: {output_path}")

    # Extract text if requested
    # if output:
    #     with pdfplumber.open(output_path) as pdf:
    #         for i, page in enumerate(pdf.pages, 1):
    #             text = page.extract_text()
    #             print(f"\n--- Page {i} ---\n{text}")

    return output_path



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unlock and extract text from password-protected PDFs")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-p", "--password", required=True, help="PDF password")
    parser.add_argument("-o", "--output", help="Output unlocked PDF path (optional)")
    parser.add_argument("-t", "--text", action="store_true", help="Extract and print text")

    args = parser.parse_args()



