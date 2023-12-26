#####################################################################
### Functions for returning PDF pages of interest
### 12/26/2023
### To be integrated with Brandon's stack
#####################################################################


# import os
import re
# import pandas as pd

# PDF text extractor
from PyPDF2 import PdfReader, PdfWriter

# Logger
from our_logger.parsearch_logger import ParsearchLogger
our_log = ParsearchLogger()


def PyPDF2_parse(input_file: str):
    '''
    Extracts PDF high-level info and contents using PyPDF2 lib

    :returns: tpl(PDF contents as string | None, page map | None)
    '''

    # Creating dict for assigning string lengths to their respective pages
    ## This is imperative for 'optimized' data pulling on page ranges
    # {page_num: len_of_cum string at end of page}
    page_char_map = dict()
    pdf_contents = ''
    with open(input_file, 'rb') as f:

        # PyPDF2 object
        py_pdf = PdfReader(f)

        # For reading each page's contents
        number_of_pages = len(py_pdf.pages)

        pdf_contents = ''
        ## FOR LOCAL DEBUGGING
        # page = py_pdf.pages[122]
        # pdf_contents += page.extract_text()
        ###
        # Extracting PDF contents
        for i in range(0, number_of_pages):
            our_log.logit('PyPDF extracting page %s' % str(i))
            page = py_pdf.pages[i]
            pdf_contents += page.extract_text()
            # Adding to page - character map
            page_char_map[str(i)] = len(pdf_contents)

    return [pdf_contents  if len(pdf_contents) > 0 else None,
            page_char_map if len(pdf_contents) > 0 else None]
            # Returning PyPDF2 object to avoid scanning PDF twice (for pdf trim)
            # py_pdf        if len(pdf_contents) > 0 else None]


def regex_get_range(search_contents: str,
                    start_identifier: str,
                    end_identifier: str,
                    page_map: dict = None):
        '''
        Use regex to locate page numbers of glossary of terms/term sheet

        search_contents (str) -> contents to search for page range
        start_identifier (str) -> Term to search for that begins page range
        end_identifier (str) -> Term to seach for the ends page range
        page_map (dict | None) -> For mapping back matching to pages for range setting, or None

        :returns: tpl(lower page bound, upper page bound)
        '''

        # START OF PAGE RANGE #
        start_matches = [ s.span() for s \
                          in re.finditer(start_identifier,
                                         search_contents,
                                         flags = re.IGNORECASE) ]        
        ### Get last instance of glassary of terms, where the string ends
        s_match_final = start_matches[-1][-1]
        # Matching the regex-found start string with its PDF page 
        s_match_key, s_match_val = min(page_map.items(),
                                       key = lambda x: abs(s_match_final - x[1]))
        # Adding 2 to makeup for pdf vs PyPDF index mismatch
        s_match_key = int(s_match_key) + 2

        # END OF PAGE RANGE #
        end_matches = [ e.span() for e \
                          in re.finditer(end_identifier,
                                         search_contents,
                                         flags = re.IGNORECASE) ]    
        ### Get last instance of glassary of terms, where the string ends
        e_match_final = end_matches[-1][-1]
        # Matching the regex-found start string with its PDF page 
        e_match_key, e_match_val = min(page_map.items(),
                                       key = lambda x: abs(e_match_final - x[1]))
        # Adding 2 to makeup for pdf vs PyPDF index mismatch
        e_match_key = int(e_match_key) + 1


        return (s_match_key, e_match_key)


def pdf_trimmer(input_file: str,
                # input_pdf_obj: object,
                page_range: tuple,
                output_file: str):
        '''
        Returns pdf file containing only the inputted page ranges of the inputted file,
        to the directory in which the function is run

        input_file (str) -> file name of pdf to be trimmed
        input+pdf_obj (object) -> PyPDF2 file object
        page_range (tpl) -> e.g. (95, 115)
        output_file (str) -> output file name

        :returns: None
        '''

        # # Creating PypDF2 object for inputted pdf
        input_pdf_obj = PdfReader(input_file, 'rb')
        # Creating the asme for outputted pdf
        output_pdf_obj = PdfWriter()

        # Iteraring through pages to be kept
        for i in range(page_range[0], page_range[1]):
          page = input_pdf_obj.pages[i]
          output_pdf_obj.add_page(page)

        with open (output_file, 'wb') as f:
             output_pdf_obj.write(f)


