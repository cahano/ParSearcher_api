#####################################################################
### Pull pdf info as xml
### 10/5/2023
### pdfminer
#####################################################################

import re
import os
import pandas as pd
from io import BytesIO, StringIO

from pdfminer.converter import TextConverter, XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


### CONVERTING PDF TO XML FORM
def get_xml(file_path):
    in_fp = BytesIO()
    lstRtn = []
    with open(file_path, 'rb') as x:
        in_fp.write(x.read())

    laparams = LAParams(all_texts=True)
    rsrcmgr = PDFResourceManager()
    outfp = StringIO()
    device = XMLConverter(rsrcmgr, outfp, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for num, page in enumerate(PDFPage.get_pages(in_fp)):
        # print(num)
        # 94 ...#
        if num == 95:
            print(num)
            interpreter.process_page(page)
            lstRtn.append(outfp.getvalue())

    device.close()
    outfp.close()
    in_fp.close()
    return lstRtn



import timeit

os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')


start_time = timeit.default_timer()



our_xml = get_xml('JPMMT_2007_ppm.pdf')[0]
# print(our_xml[0:1000])
# print(our_xml[-50:-2])
# print(type(our_xml))
# print()
# print()


import xml.etree.ElementTree as ET

# Adding closing node if it does not exist
temp_xml = ET.fromstring(our_xml + '</pages>')
        #    if our_xml.find('</pages>') != -1 \
        #    else ET.fromstring(our_xml) 


### bbox = [left, top, right, bottom]
##### ITERATE THROUGH EACH BOUNDING BOX


# Creating list of all '<text>' XML nodes (i.e. the bbox), and excluding attribute-less nodes
## THIS IS HOW CURRENT PPM XML IS STRUCTURED
### WHICH MAY CHANGE BY PDF, OR EVEN BY PAGE.....
xml_texts = [ x for x in temp_xml[0].iter('text') if x.attrib != {} ]


### THIS WILL BE INTEGRAL PARTS OF THE PARSER
#### SHOULD BASICALLY MATCH PDF FORMATTING CONSTANTS (i.e. col height in px), BY DEFINITION

# pixal-spacial threshold for determining if next char is from the same cell
CELL_THRESHOLD_LEFT = 12
# pixal-spacial threshold for determining if next char is from the same row
### THRESHOLD OF 15 IS TOO BIG (i.e. col headers are merged w/ col vals)
### THRESHOLD OF 14 APPEARS TO BE THE MAGIC NUMBER
###     -> i.e. includes last col values (e.g. 'Total') which are slightly more vertically spaced,
###        but excludes col headers
CELL_THRESHOLD_BOTTOM = 14
# Certain cols seem to have a smaller vertical space than others
### ESSENTIALLY AN EDGE CASE
EDGE_CASE_BOTTOM = 8
# Char denoting table split


### THE BOUNDS FOR COL VALS WITH SINGLE DIGITS IS TOO SMALL
##### NEED TO HANDLE THIS EDGE CASE

# Stores tables (i.e. cols split into respective tables) 
parent_cols = []
# Stores cols
col = []
# Stores cell vals
cell = ''
# LOOPING THROUGH XML CONTENTS
for i in range(1, len(xml_texts[0:1000])):

    ## Relevant info for each XML node ##

    # Bounding boxes
    _cur_bbox_l, _cur_bbox_t, _cur_bbox_r, _cur_bbox_b = xml_texts[i]\
                                                         .attrib['bbox'].split(',')
    _prev_bbox_l, _prev_bbox_t, _prev_bbox_r, _prev_bbox_b = xml_texts[i-1]\
                                                             .attrib['bbox'].split(',')

    # Font sizes
    _cur_font_size = xml_texts[i].attrib['size']
    _prev_font_size = xml_texts[i-1].attrib['size']
    
    # Contents
    _cur_text = xml_texts[i].text
    _prev_text = xml_texts[i-1].text

    ######################################


    print('XML CONTENT:')
    print(xml_texts[i].attrib)
    print()
    print(xml_texts[i].text)
    print('-----------------')
    print()


    ## Rebuilding table ##

    # Combining chars within the same cell
    ## Represented as:
    #       bottom space between characters less than CELL_THRESHOLD_BOTTOM
    #       left space between characters less than CELL_THRESHOLD_LEFT
    if abs(float(_prev_bbox_b) - float(_cur_bbox_b)) < CELL_THRESHOLD_BOTTOM \
    and ( abs(float(_prev_bbox_l) - float(_cur_bbox_l)) < CELL_THRESHOLD_LEFT ):
        
        # FOR GETTING SUFFICENTLY SMALL (e.g. single-digit) COL VALUES
        ## THIS IS WHEN THE BOTTOM SPACE BETWEEN CHARS IS SMALLER THAN 
        if abs(float(_prev_bbox_b) - float(_cur_bbox_b)) > EDGE_CASE_BOTTOM:

            # cell CAN be empty
            if cell == '':
                cell = _prev_text
            else:
                cell += _prev_text

            # Storing cell to col
            col.append(cell)
            # Resetting cell val
            cell = ''
            
        else:
            cell += _prev_text

    # Isolating completed cell value and adding to col
    ## represented as:
    #       bottom space between chars LT CELL_THRESHOLD_BOTTOM
    #       left space between chars is GT CELL_THRESHOLD_LEFT
    elif abs(float(_prev_bbox_b) - float(_cur_bbox_b)) < CELL_THRESHOLD_BOTTOM \
    and ( abs(float(_prev_bbox_l) - float(_cur_bbox_l)) > CELL_THRESHOLD_LEFT ):

        # Adding last char of cell value before splitting off
        cell += _prev_text
        # Adding to col
        col.append(cell)
        # Resetting cell val
        cell = ''


    # Isolating col of completed cell values
    ## represented as
    #       bottom space between chars GT CELL_THRESHOLD_BOTTOM
    #       left space between chars is GT CELL_THRESHOLD_LEFT
    elif abs(float(_prev_bbox_b) - float(_cur_bbox_b)) > CELL_THRESHOLD_BOTTOM \
    and abs(float(_prev_bbox_l) - float(_cur_bbox_l)) > CELL_THRESHOLD_LEFT:
        
        # Adding last char of last cell of col 
        cell += _prev_text

        # Adding last cell of cal
        col.append(cell)

        # Assigning col to parent_cols, which will form the dataframe
        parent_cols.append(col)
        # Resetting cell val
        cell = ''
        # Resetting col vals
        col = []

    ######################################



#### NEED TO DETERMINE IF ISSUES OCCUR IN THE ABOVE (CELL FOUNDATION)
#### OR BELOW (preferably) IN AGGREGATING TABLES PROPERLY


### LOOPING THROUGH ALL CONVERTED COLS ###

# Each annex A table has 4 cols, but a 5th will be added (col headers)
TABLE_SPLIT = 9
COL_HEADS = ['# of Mtg Loans',
             '$ Agg Principal Bal Oustanding',
             '% Agg Principal Bal Oustanding']

titles = []
index_titles = []
final_list = []
### SPLITTING TABLES AND BUILDING DF
#### CURRENTLY LOOPING THROUGH RESULTS AFTER ALL XML DATA IS PARSED
#### IS MORE EFFICIENT TO DO THIS IN THE ABOVE FOR LOOP
###### WILL EVENTUALLY DO THIS
for i in range(0, len(parent_cols) - 1):

    # Storing previous, current, and next values
    ## each will be a list, which can consist of:
    ##      -> single page title
    ##      -> col headers
    ##      -> col values
    ##      -> footnote
    ##      -> '____' (e.g. decorative line between two tables on PDF)
    _prev_col = parent_cols[i-1] \
                if i > 0 \
                else None
    _curr_col = parent_cols[i]
    _next_col = parent_cols[i+1]


    ### THIS WILL BE A LOT OF HARDCODING FOR NOW ###

    # Omitting unwanted info
    ## 'PM' and 'AM' indicate list of vals composing timestamps/serial # atop each PDF page
    ## 'https' indicates sec link at the bottom of each PDF page
    if ' PM' in _curr_col[0] \
    or ' AM' in _curr_col[0] \
    or 'https' in _curr_col[0] \
    or _curr_col == []:
        continue

    # Getting titles
    ## '(1) -' is indicative of an Annex A table title
    ##      -> e.g. 'Current Mortgage Rates(1) - Aggregate Pool'
    # Index title comes immediately after table title
    if '(1) -' in _curr_col[0]:

        # print('FORWARD LOOKING VALS')
        # print(_curr_col[0])
        # print(_next_col[0])
        # print(parent_cols[i+2])
        # print(parent_cols[i+3])
        # print(parent_cols[i+4])
        # print(parent_cols[i+5])
        # print(parent_cols[i+6])
        # print(parent_cols[i+7])
        # print(parent_cols[i+8])
        # print(parent_cols[i+9])
        # print('---------------------------')
        # print()

        df_vals = []
        ## THE '9' VALUE IDICATES THE NUM OF COL LIST VALUES
        ## THE '2" SKIPS CURRENT TITLE AND INDEX TITLE 
        for j in range(i + 2, i + 9):

            # print('IN J LOOP')
            # print(parent_cols[j])
            # print(parent_cols[j][0][0 : parent_cols[j][0].find(' ')+1])
            # print(parent_cols[j][0][0 : parent_cols[j][0].find(' ')] == 'Percent')
            # print('++++++++++++')

            # SKIPPING COL HEADERS
            ### OBV AWFULLY HARDCODED LOGIC
            ### CHECKING IF FIRST WORD IS THAT OF A COL HEADER
            ### ASSUMES ONLY COL HEADERS START WITH THESE WORDS
            ##### WHICH MAY ACTUALLY BE TRUE
            if parent_cols[j][0] == 'Number' \
            or parent_cols[j][0] == 'Aggregate' \
            or parent_cols[j][0] == 'Percent' \
            or parent_cols[j][0][0 : parent_cols[j][0].find(' ')] == 'Percent':
                continue
            elif len(parent_cols[j]) > 1 \
            and parent_cols[j][1] == '(1)':
                footnote = '(1) ' + parent_cols[j][-1].rstrip(' ')\
                                                     .rstrip('\n')
            else:
                df_vals.append(parent_cols[j])

        # print()
        # print('DF VALS')
        # print(df_vals)
        # print()

        # Based on title being found, grab cols
        ## VERY HARDCODED
        ### NEED TO MAKE THIS WORK BASED ON SOME INPUT
        #### LIKE COL NUMS
        # if i < len(parent_cols) - 8:
        temp_df = pd.DataFrame(data = df_vals).T
        temp_df.index.name = _next_col[0]
        temp_df.columns = [''] + COL_HEADS
        # Appending [title, df, footnote]
        final_list.append([_curr_col[0].rstrip('\n'),
                            temp_df,
                            footnote])



# for i in final_list:
#     print('INDIVIDUAL TABLE OBJECT (i.e. [title, df, footnote])')
#     print(i[0])
#     print(i[1])
#     print(i[2])
#     print('~~~~~~~~~~~~~~~~~~~~~~~~~')
#     print()

# print()
# print()
# print('FINAL OUTPUT')
# print(final_list[0][0])
# print()
# print(final_list[0][1])
# print(final_list[0][1].columns)
# print()
# print(final_list[0][2])


## ITERATING THROUGH TABLE COLS
### SPLITTING 



end_time = timeit.default_timer()

print()

print()
print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))



### OLD

# # FOR GETTING SUFFICENTLY SMALL (e.g. single-digit) COL VALUES
# elif abs(float(_prev_bbox_b) - float(_cur_bbox_b)) > CELL_THRESHOLD_BOTTOM \
# and ( abs(float(_prev_bbox_l) - float(_cur_bbox_l)) < CELL_THRESHOLD_LEFT ):

#     if cell == '':
#         cell = _prev_text
#     else:
#         cell += _prev_text

#     col.append(cell)
#     cell = ''


