#####################################################################
### Combining business logic (constants) and parsers
### 10/5/2023
### Will be called -async- with a Tornado worker
#####################################################################

import os
import timeit

# Importing parsing tools
from lib.pypdf_regex_camelot import (PyPDF2_parse,
                                     regex_get_range,
                                     camelot_to_xlsx)
# Importing constants (biz logic)
from constants.biz_logic import RMBSLogic
# Logger
from our_logger.parsearch_logger import ParsearchLogger
our_log = ParsearchLogger()


def vanillot_ppm(input_pdf: str,
                 input_path: str,
                 output_name: str):
    '''
    Runs PyPDF2, Regex, and Camelot on inputted RMBS PPM and extracts
    Glossary of Terms/Term Sheet & Annex Tables

    input_pdf (str) -> name of pdf file (inclusive of .pdf)
    input_path (str) -> path to file (important for temp file server procs)
    output_name (str) -> Output file name (inclusive of file ext (e.g. '.xlsx'))

    :returns: None -> uploads outputted file to inputted path
    '''

    os.chdir(input_path)

    start_time = timeit.default_timer()
    our_log.logit('BEGINNING PDF PROCESSING')


    # Pulling PDF contents as string, page map as dict #
    ppm_contents, ppm_page_map = PyPDF2_parse(input_pdf)

    # Using Regex to identify page ranges #
    # For term sheet
    terms_range = regex_get_range(ppm_contents,
                                  RMBSLogic.term_sheet_start,
                                  RMBSLogic.term_sheet_end,
                                  ppm_page_map)
    # For annex tables
    ### NEED LOGIC FOR ENSURING THE RANGES ONLY RETURN THE SOONEST MATCH AFTER THE STARTING ONE
    annex_range = regex_get_range(ppm_contents,
                                  RMBSLogic.annex_start,
                                  RMBSLogic.annex_end,
                                  ppm_page_map)

    # Applying camelot to the returned table ranges #
    term_sheet_dfs = camelot_to_xlsx(r'',
                                     input_pdf,
                                     r'',
                                     output_name,
                                     '{}-{}, {}-{}'.format(terms_range[0], terms_range[1],
                                                           annex_range[0], annex_range[1]))
    

    our_log.logit('PDF PROCESSING COMPLETE')
    # Ending timer
    end_time = timeit.default_timer()
    our_log.logit('~~~ runtime: %f sec ~~~' % (end_time - start_time))



#### TESTING

# import timeit

# ## FOR LOCAL TESTING
# # # Setting wd to get pdf
# # os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')

# # Starting timer
# start_time = timeit.default_timer()

# vanillot_ppm(
#     'JPMMT_2007_ppm.pdf',
#     r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs',
#     'xlsx_tester.xlsx'
#              )

# # Ending timer
# end_time = timeit.default_timer()

# print()
# print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))

