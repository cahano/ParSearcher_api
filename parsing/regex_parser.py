import os
import sys
import logging
from typing import List, Tuple

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

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

things_we_want: List[str] = consts.unique_tag_list()


def is_valuable_page(s: str) -> Tuple[str, bool]:
    """
        Returns the string idx of strings we want
    """

    # TODO build this out where explore the page string and find a more accurate table index
    # currently this function just searches for notable page titles

    # TODO rename to parse_page, use is_valuable later

    for t in things_we_want:
       # TODO: what if there are multple things on this page?
       if s.find(t):
           return t, True
    return "", False


def read_pdf() -> models.PDF:

    log.info(f"Getting PDF...")
    pdf = models.PDF(
        name="jpm_pdf",  # create helper function to get and clean name
        request_id="none",
        create_date=util.datetime_to_iso()
    )
    with open(SAMPLE_PDF, 'rb') as f:
        py_pdf: PdfReader = PdfReader(f)

        for py_page in py_pdf.pages:
            page: models.Page = models.Page(
                # TODO: This might slow, check if there is a better way to get number
                page_number=py_pdf.get_page_number(py_page),
                page_contents=py_page.extract_text(),
            )
            page_tag, possilbe_table = is_valuable_page(page.page_contents)
            page.possible_table = possilbe_table
            page.page_tag = page_tag
            pdf.pages.append(page)


    log.info(f"Extracted {pdf.total_pages} pages from PDF")
    return pdf


def parse_regex():
    """
        Parse PDF strings with regex
    """
    
    log.info(f"Starting regex parsing")

    pdf: models.PDF = read_pdf()
    pages = [p for p in pdf.pages if p.possible_table]

    # current state of this is that we basically mark any page that mentions annex A as notable...
    # which is wrong.

    for page in pages:
        log.info(f"Found notable page: {page.page_tag}, {page.page_number}")

    return


# TODO remove this once integrated with API
# api will call parse_regex
if __name__ == "__main__":
    parse_regex()