import os
import sys
import logging
from typing import List

# Needed to add this to ensure logger imported succesfully
## something with my file structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from PyPDF2 import PdfReader
import models
import consts
import util
# TODO fix relative imports
# from .models import Page, PPM_Schema, PDF 
# from .consts import unique_tag_list
# from .util import datetime_to_iso, chunker

SAMPLE_PDF="../JPMMT_2007_ppm.pdf"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

things_we_want: List[str] = consts.unique_tag_list()

def read_pdf() -> PDF:

    log.info(f"Getting PDF...")
    pdf = models.PDF(
        name="jpm_pdf",  # create helper function to get and clean name
        request_id="none",
        create_date=util.datetime_to_iso()
    )
    with open(SAMPLE_PDF, 'rb') as f:

        # PyPDF2 object
        py_pdf = PdfReader(f)

        for page_idx in range(py_pdf.numPages):
            page = py_pdf.pages[page_idx]
            pdf.pages.append(Page(
                page_id=page_idx,
                page_contents=page.extract_text()
            ))

    log.info(f"Extracted {pdf.total_pages} pages from PDF")
    return pdf


def is_valuable_tag(s: str) -> bool:
    return s in things_we_want

def parse_regex():
    
    log.info(f"Starting regex parsing")

    pdf: PDF = read_pdf()



    return


# TODO remove this once integrated with API
# api will call parse_regex
if __name__ == "__main__":
    parse_regex()