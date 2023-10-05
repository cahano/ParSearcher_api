#####################################################################
### Pull pdf text, scan for table range, pull table funcs
### 10/5/2023
### PyPDF2, regex, camelot
#####################################################################

import os
import re
import pandas as pd

# PDF text extractor
from PyPDF2 import PdfReader
# PDF table extractor
import camelot

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

    return (pdf_contents \
            if len(pdf_contents) > 0 \
            else None,
            page_char_map \
            if len(pdf_contents) > 0 \
            else None)


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


def camelot_to_xlsx(input_path: str,
                    input_filename: str,
                    output_path: str,
                    output_filename: str,
                    page_range: str):
    '''
    Converts pdf tables to pd.df, then to an xlsx output file;
    for each pdf table extracted, a sheet is appended to the xlsx output file

    input_path -> path to be parsed pdf location
    input_filename -> name of to be parsed pdf
    output_path -> path to xlsx output location
    output_filename -> name of output xlsx
    page_range -> str containing one of:
                  single page (e.g. '1'), range of pages (e.g. '2-5'), or all pages (e.g. 'all')
                  for table(s) intended for extraction
    '''
    

    our_log.logit('Extracting tables from %s' % input_filename)

    # Running extraction
    cam_tabs = camelot.read_pdf(os.path.join(input_path,
                                                input_filename),
                                 pages = page_range,
                                 flavor ='stream',
                                 edge_tol = 500)


    # Checking for table extraction(s)
    if len(cam_tabs) == 0:        
        our_log.logit('*** NO tables extracted by camelot! ***')
        return None
    # logging input info
    our_log.logit('camelot succesfully extracted {} table(s) from {}'.format(len(cam_tabs),
                                                                          input_filename))

    # Create a Pandas Excel writer using XlsxWriter as the engine
    cam_writer = pd.ExcelWriter(os.path.join(output_path,
                                             output_filename),
                                engine = 'xlsxwriter')

    # for creating sheet names
    sheet_count = 0
    # Iterating through camelot-extracted tables
    for table in cam_tabs:

        # Storing extracted table
        ext_df = table.df

        # our_log.logit(ext_df)

        # Convert the dataframe to an XlsxWriter Excel object
        ext_df.to_excel(cam_writer,
                        sheet_name = 'Sheet ' + str(sheet_count))

        sheet_count += 1

    # Close the Pandas Excel writer and output the Excel file
    cam_writer.close()




###### TESTING

# import timeit

# ## FOR LOCAL TESTING
# # Setting wd to get pdf
# os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')

# # SIMULATE PyPDF2 parser + page map
# # Read in file
# with open('ppm_output.txt', 'r', encoding='utf-8') as txt_file:
#     ppm_txt = txt_file.read()


# ppm_page_map = {'0': 3267, '1': 6293, '2': 8436, '3': 10969, '4': 12935, '5': 14132, '6': 17205, '7': 24739, '8': 33816, '9': 33934, '10': 38509, '11': 42895, '12': 47497, '13': 52461, '14': 58769, '15': 62243, '16': 65792, '17': 68752, '18': 74696, '19': 80075, '20': 85784, '21': 91441, '22': 97026, '23': 103338, '24': 110041, '25': 112306, '26': 113817, '27': 115333, '28': 116855, '29': 118377, '30': 119899, '31': 
#                 124029, '32': 129513, '33': 136153, '34': 141792, '35': 146678, '36': 152878, '37': 159015, '38': 163475, '39': 169500, '40': 175303, '41': 181752, '42': 187304, 
#                 '43': 192752, '44': 197611, '45': 203514, '46': 209783, '47': 215485, '48': 219049, '49': 224478, '50': 230118, '51': 236284, '52': 242096, '53': 247613, '54': 253717, '55': 259162, '56': 264303, '57': 270160, '58': 276224, '59': 282838, '60': 288465, '61': 293730, '62': 299404, '63': 303785, '64': 308960, '65': 315165, '66': 319496, '67': 326844, '68': 332477, '69': 334117, '70': 335814, '71': 342046, '72': 348029, '73': 354750, '74': 361712, '75': 367592, '76': 373577, '77': 378437, '78': 381918, '79': 385575, '80': 389097, '81': 392952, '82': 396891, '83': 401062, '84': 404924, '85': 408320, '86': 412139, '87': 416208, '88': 420435, '89': 424403, '90': 427830, '91': 432371, '92': 436003, '93': 436579, '94': 439441, '95': 442075, '96': 444299, '97': 446524, '98': 448886, '99': 450171, '100': 452787, '101': 455240, '102': 457325, '103': 458848, '104': 461531, '105': 464105, '106': 466324, '107': 468730, '108': 470211, '109': 472962, '110': 475521, '111': 477725, '112': 480180, '113': 481233, '114': 483949, '115': 486507, '116': 488715, 
#                 '117': 491071, '118': 492349, '119': 497727, '120': 503130, '121': 503900, '122': 506774, '123': 509871, '124': 513197, '125': 516388, '126': 517817, '127': 519200, '128': 521095, '129': 522623, '130': 525007, '131': 526928, '132': 527771, '133': 531518, '134': 537665, '135': 542888, '136': 548686, '137': 554426, '138': 558614, '139': 564670, '140': 570031, '141': 576535, '142': 583039, '143': 589942, 
#                 '144': 595391, '145': 601252, '146': 608136, '147': 614072, '148': 620934, '149': 627720, '150': 632669, '151': 637350, '152': 643512, '153': 648814, '154': 655090, '155': 661946, '156': 669035, '157': 673840, '158': 677976, '159': 681569, '160': 686831, '161': 692737, '162': 699002, '163': 704749, '164': 711705, '165': 718619, '166': 724066, '167': 730116, '168': 736164, '169': 741029, '170': 745978, 
#                 '171': 751872, '172': 757208, '173': 764440, '174': 770342, '175': 776451, '176': 782705, '177': 787927, '178': 794084, '179': 801368, '180': 807546, '181': 814304, '182': 820313, '183': 826217, '184': 832477, '185': 838735, '186': 846010, '187': 852458, '188': 858870, '189': 865517, '190': 872196, '191': 879347, '192': 886081, '193': 893109, '194': 899726, '195': 906711, '196': 912630, '197': 917450, 
#                 '198': 924136, '199': 930639, '200': 937808, '201': 944793, '202': 951408, '203': 957170, '204': 963818, '205': 970889, '206': 977851, '207': 984441, '208': 990706, '209': 997720, '210': 1004782, '211': 1010657, '212': 1017213, '213': 1024295, '214': 1029752, '215': 1036336, '216': 1041385, '217': 1047163, '218': 1054347, 
#                 '219': 1060354, '220': 1066596, '221': 1067920, '222': 1071629, '223': 1073719, '224': 1075386}

# # ##

# # Starting timer
# start_time = timeit.default_timer()

# # Pulling PDF contents as string #
# # ppm_contents = PyPDF2_parse('JPMMT_2007_ppm.pdf')


# # Using Regex to identify page ranges #

# # For term sheet
# terms_range = regex_get_range(ppm_txt,
#                               r'GLOSSARY OF DEFINED TERMS',
#                               r'Annex A',
#                               ppm_page_map)
# # For annex tables
# ### NEED LOGIC FOR ENSURING THE RANGES ONLY RETURN THE SOONEST MATCH AFTER THE STARTING ONE
# annex_range = regex_get_range(ppm_txt,
#                               r'Annex A',
#                               r'Annex [BCD][-][1]', # matches 'B-1' in ppm
#                               ppm_page_map)

# print(terms_range)
# print(annex_range)

# # # Applying camelot to the returned table ranges #
# # term_sheet_dfs = camelot_to_xlsx(r'',
# #                                  'JPMMT_2007_ppm.pdf',
# #                                  r'',
# #                                  'parsed_terms.xlsx',
# #                                  '{}-{}, {}-{}'.format(terms_range[0], terms_range[1],
# #                                                        annex_range[0], annex_range[1]))


# # Ending timer
# end_time = timeit.default_timer()

# print()
# print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))
