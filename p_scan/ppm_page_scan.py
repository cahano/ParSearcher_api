#####################################################################
### PyPDF2-based function for returning PDF of ONLY annex of interest
### 12/26/2023
### To be integrated with Brandon's stack
#####################################################################

# import sys
import os
import timeit

# # Needed to add this to ensure logger imported succesfully
# ## something with my file structure
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))

# print(SCRIPT_DIR)
# print(os.getcwd())

# Importing parsing tools
from page_scan_utils import ( PyPDF2_parse,
                              regex_get_range,
                              pdf_trimmer )
# Importing constants (business logic logic)
from page_scan_consts import RMBSLogic
# Logger
from our_logger.parsearch_logger import ParsearchLogger
our_log = ParsearchLogger()


def ppm_page_finder(input_pdf: str,
                    input_path: str,
                    output_name: str):
    '''
    Runs PyPDF2 and Regex on inputted RMBS PPM,
    returns pdf file containing only relevant annex tables

    input_pdf (str) -> name of pdf file (inclusive of .pdf)
    input_path (str) -> path to file (important for temp file server procs)
    output_name (str) -> Output file name (inclusive of file ext (e.g. '.xlsx'))

    :returns: None -> uploads outputted file to inputted path
    '''

    os.chdir(input_path)

    start_time = timeit.default_timer()
    our_log.logit('BEGINNING PyPDF2 PROCESSING')

    # Pulling PDF contents as string, page map as dict #
    ppm_contents, ppm_page_map = PyPDF2_parse(input_pdf)

    # # Using Regex to identify page ranges #
    # # For term sheet
    # terms_range = regex_get_range(ppm_contents,
    #                               RMBSLogic.term_sheet_start,
    #                               RMBSLogic.term_sheet_end,
    #                               ppm_page_map)
    # For annex tables
    ### NEED LOGIC FOR ENSURING THE RANGES ONLY RETURN THE SOONEST MATCH AFTER THE STARTING ONE
    annex_range = regex_get_range(ppm_contents,
                                  RMBSLogic.annex_start,
                                  RMBSLogic.annex_end,
                                  ppm_page_map)

    # Returning trimmed pdf file #
    pdf_trimmer(input_pdf,
                # pdf_obj,
                (annex_range[0], annex_range[1]),
                output_name)
    

    our_log.logit('PyPDF2 PROCESSING COMPLETE')
    # Ending timer
    end_time = timeit.default_timer()
    our_log.logit('~~~ runtime: %f sec ~~~' % (end_time - start_time))



### TESTING

# import timeit

# ## FOR LOCAL TESTING
# # # Setting wd to get pdf
# # os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')

# # Starting timer
# start_time = timeit.default_timer()

# ppm_page_finder(
#     'JPMMT_2007_ppm.pdf',
#     r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs',
#     'annex_a_test.pdf'
#              )

# # Ending timer
# end_time = timeit.default_timer()

# print()
# print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))

