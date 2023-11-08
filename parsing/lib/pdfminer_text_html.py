#####################################################################
### Pull pdf info as xml
### 10/5/2023
### pdfminer
#####################################################################

import re
import os
import pandas as pd
from io import BytesIO, StringIO

from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


### CONVERTING PDF TO HTML FORM
def get_html(file_path):
    in_fp = BytesIO()
    lstRtn = []
    with open(file_path, 'rb') as x:
        in_fp.write(x.read())

    laparams = LAParams(all_texts=True)
    rsrcmgr = PDFResourceManager()
    outfp = StringIO()
    device = HTMLConverter(rsrcmgr, outfp, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for num, page in enumerate(PDFPage.get_pages(in_fp)):
        print(num)

        # 94 works 100% #
        # 95 breaks #
        # 96 works for ONE of the two tables #
        # 97 HAS POTENTIAL #
        if num == 95:
            print(num)
            print(lstRtn)
            interpreter.process_page(page)
            lstRtn.append(outfp.getvalue())

    device.close()
    outfp.close()
    in_fp.close()
    return lstRtn




# #### CLEANING CONVERTED HTML CONTENTS TO GET TABLES

# from bs4 import BeautifulSoup

# import timeit

# os.chdir(r'C:\Users\owen_\Desktop\CareerRel\O1\py_related\full_stack\ParseDF\test_docs')


# start_time = timeit.default_timer()

# x = get_html('JPMMT_2007_ppm.pdf')
# # print(x)
# # print()
# # print()

# soup = BeautifulSoup(x[0], 'html.parser')
# ########## HARDCODE div
# tag = soup.find_all('div')
# print(soup.prettify())

# # The four below lists compose all elements needed to rebuild a table
# titles = []
# col_sets = []
# col_headers = []
# # This will house, together, each set of cols that compose a table
# ## e.g.   [ [[tab1_col1], [tab1_col2], ...], [[tab2_col1], [tab2_col2], ...] ]
# tables_list = []
# df_list = []
# footnotes = []
# # Looping through each <div> tag, which may include:
# ##      a title, a column, a column title, or a footnote
# for i in tag:
#     print(i)
#     print()

#     ### HANDLING TITLE
#     # TABLE TITLES HAVE HEIGHT OF 9px AND FOLLOWED by '<br/>'
#     ########## HARDCODE regex
#     if re.search(r'height:9px;">((.|\n)*)<br\/>', str(i)):

#         # print('XXXXX TITLE MATCH XXXXX')
#         # print(i)

#         # Current matched value (could be one of title, column, col header, footnote, etc)
#         ########## HARDCODE regex
#         _matched_val = re.search(r'font-size:9px">((.|\n)*)<br\/>', str(i)).group(1)
#         # Storing current div's CSS left positioning
#         ########## HARDCODE regex
#         _match_left_pos = re.search(r'left:(\d+)px;', str(i)).group(1)
#         _match_height = re.search(r'height:(\d+)px;', str(i)).group(1)
#         # If CSS left positioning is less than 100, it's a title
#         ########## HARDCODE position threshold
#         # Titles
#         if float(_match_left_pos) < 100:
#             titles.append(_matched_val.rstrip('\n'))
        
#         continue


#     # EDGE CASE EXISTS WHERE ONE FUCKING COL OF VALS HAS ONLY ONE SPAN
#     ## THE REST HAVE TWO
#     ### solved by count of '<br/>' > 3; eseentially a proxy for col length
#     #### therefore, a col of values will have greater than 3 of these....
#     if str(i).count('font-size:9px') > 1 \
#     or str(i).count('<br/>') > 3:
        
#         # # ATTEMPTING TO WEED OUT COL HEADERS PASSING THROUGH EDGE CASE
#         # if str(i).count('span') > 3 and str(i).lower().find('total') == -1:
#         #     continue

#         # Matching ENTIRE col
#         _matched_col = re.search(r'>((.|\n)*)<br\/>', str(i))

#         # print('**** MATCHED COL *******')
#         # print(_matched_col)

#         # Looping through each col value (re match split by <br/>)
#         _clean_col = []
#         ########## HARDCODE string logic
#         for col_val in _matched_col.group(1).split('<br/>'):

#             # print('**** COL VALUE ****')
#             # print(col_val)
            
#             # clean individual col value
#             ########## HARDCODE string logic
#             clean_col_val = col_val.replace('<br/>', '')\
#                                    .replace('\n', '')\
#                                    .replace('%', '')
#             ### WEEDING OUT COL HEADERS
#             if ('Aggregate' in clean_col_val \
#             or 'Principal' in clean_col_val \
#             or 'Balance' in clean_col_val) \
#             and '(1)' not in clean_col_val:
#                 print('WEEDING OUYT COL HEADERS')
#                 print(clean_col_val)
#                 break

#             ## HANDING COL VALUES & FOOTNOTES
#             # if (1), it's a footnote
#             ########## HARDCODE string logic
#             if clean_col_val.find('(1)') != -1:
#                  footnotes.append(clean_col_val[clean_col_val.rfind('>')+1 : \
#                                                len(clean_col_val)].rstrip(' '))
#             # if there are more than 1 '>' it's a value that needs cleaning
#             ## remove all inline CSS from col value
#             elif clean_col_val.count('>') > 0:
#                  _clean_col.append(clean_col_val[clean_col_val.rfind('>')+1 : \
#                                                  len(clean_col_val)])
#             # otherwise, it's an already cleaned col value
#             else:
#                 _clean_col.append(clean_col_val)


#         # print('XXXXXXXX CLEANED COL XXXXXXXXXX')
#         # print(_clean_col)
#         # print('XXXXXXXXXXXXXX')
#         ### HANDLING TABLE PARTITIONING
#         #### because the <div>s do not do this as nicely as we'd like
#         # '__' signifies end of table
#         if (len(tables_list) > 0 \
#         and len([ x for x in _clean_col if x.find('__') != -1 ]) > 0) \
#         or (len(tables_list) == 4):
#             # append cols to final df for conversion
#             df_list.append(tables_list)
#             # Reset tables list for next table
#             tables_list = []
#         ####### THIS SEEKS TO REMOVE COL HEADERS THAT SNEAK THROUGH
#         elif _clean_col == []:
#             print('EMPTY CLEAN')
#             print(_clean_col)
#             continue
#         else:
#             print('XXXX APPENDING CLEAN COL')
#             print(_clean_col)
#             # Add col value if end of table (e.g. '__') is not detected
#             tables_list.append([ x for x in _clean_col if x.find('__') == -1 ])
#         print('~~~~~~~~~~ TQBLES LIST ~~~~~~~~~~')
#         print(tables_list)
#         print(df_list)

# # Looping through collection of titles, tables, and footnotes
# final_dfs = []
# for title, table, footnote in zip(titles, df_list, footnotes):
#     print(title)
#     print(table)
#     print(footnote)
#     print()
#     print('---------------')
#     # Creating dataframe
#     temp_df = pd.DataFrame(table).T
#     temp_df.columns = ['',
#                        '# of Mtg Loans',
#                        'Agg $ Outstanding',
#                        'Agg % outstanding']

#     # Append list of [title, df, footnote(s)]
#     final_dfs.append([title, temp_df, footnote])

# # Last cleanups
# for q in final_dfs:
#     ## If sum of % col is NoneType, set it to 100
#     # Subtract one to match pd index
#     if not q[1].at[len(q[1])-1, 'Agg % outstanding']:
#         q[1].at[len(q[1])-1, 'Agg % outstanding'] = 100.00

#     print(q[1])
#     print()

# end_time = timeit.default_timer()

# print()

# print()
# print('~~~~~~~~~ runtime: %f ~~~~~~~~~' % (end_time - start_time))





### SCRAPS


# if col_vals_final[i-1][0].title() == col_vals_final[i-1][0] \
# and not col_vals_final[i-1][0].replace(',', '').replace('.', '').replace(' - ', '').replace('%', '').isdigit() \
# and not col_vals_final[i+1][0].replace(',', '').replace('.', '').replace(' - ', '').replace('%', '').isdigit() \
# and col_vals_final[i][0].find('(') != -1 and col_vals_final[i][0].find(')') != -1:
#     print('IN TITLE CONDITION')
#     print(col_vals_final[i-1])
#     title_final.append(col_vals_final[i-1][0])


#     cleaned_row = str(i).split('<br/>')
#     row_vals = []
#     for val in cleaned_row:
#         print('Uncleaned value:', val)
#         # Testing for numeric strings
#         if val.rstrip('\n').replace(',', '').replace('.', '').isdigit():
#             row_vals.append(val.rstrip('\n').replace(',', ''))

#         # Capturing row headers e.g. '1000 - 2000'
#         elif val.find(' - ') != -1:
#             ### FIRST ROWS HAVE THE SPAN FORMATTING - USEFUL FACT
#             if val.find('px"') != -1:
#                 row_vals.append(val[val.find('>')+1: -1].rstrip('\n'))
#             else:
#                 row_vals.append(str(val).rstrip('\n'))

#         # HANDLING LEADING ROW VALS/COL HEADERS (I THINK)
#         elif val.find('px"') != -1:
#             print('head case')
#             # print(val)
#             print(val[val.find('>')+1 : -1].rstrip('\n'))
#             # Collect data from after '>' to End of string, remove '\n' if found
#             row_vals.append(val[val.find('>')+1: -1].rstrip('\n'))
            

#         # clean_val = re.search(r'>(.*)\\n', str(val)).group(1) \
#         #             if re.search(r'>(.*)\\n', str(val)) \
#         #             else None
#         # print('Cleaned Value: ', clean_val)
#         # if clean_val:
#         #     row_vals.append(clean_val)

#     row_vals_final.append(row_vals)

# print(row_vals_final)

    # cleaned_row_final = [ x for x in cleaned_row ]

    #### THIS IS GREAT PROGRESS

    # row_vals.append(i.split('<br/>'))
    ##### ROWS ARE CLUMPED IN TWOS:
    # re_match_1, re_match_2 = re.search(r'>(.+?)<br\/>(.+?)\\n<br\/>', str(i)).group(1), \
    #                          re.search(r'>(.+?)<br\/>(.+?)\\n<br\/>', str(i)).group(2)
    # print(re_match_1, re_match_2)


    # print(i)
    # print()

# print(final_p)

### REGEX SEARCHES

# # Searching for row items: ....'>some content<br/>'
# y = [z.group() for z in re.finditer( r'\>(.*)<br>/g', x[0] )]

# print(y)



# final_p = [z.span for z in re.finditer( r'<br\/>(.*)\\n/g', x[0] )]

# NEED TO SPLIT EACH TABLE
# END IF '_________' OR '(1) ....' [footnote]
## THIS APPROACH RELIES ON THE EXISTANCE OF A FOOTNOTE DENOTED BY '(\d)'
## OR '_________'

# ### THEN TITLE

# #### ALL OF TABLES COL HEADERS FALL BETWEEN COLS 1 AND 2

# # Storing table row values
# col_vals_final = []
# # Storing col headers
# col_heads = []
# # Iterating though 'span' matches
# for i in tag:
#     print()
#     print()
#     print('NEXT TAG')
#     print(i)
#     print()
#     # print(str(i).split('<br/>'))

#     # Skipping unneeded values
#     ## time vals
#     ## vals with '_'
#     ### Basically edge cases...
#     if (str(i).find(':') != -1 \
#     and str(i).lower().find(' pm') != -1) \
#     or (str(i).find('_') != -1):
#         continue

#     # match anything between '>...</span>' including '\n'
#     _re_col = re.search(r'>((.|\n)*)<\/span>', str(i))
#     if _re_col:
#         # print(_re_row.groups())
#         _cols = _re_col.group(1).split('\n<br/>')
#         # Removing '' as last element if it exists (which results from trailing '\n<br/>')
#         if '' in _cols:
#             _cols.pop()
#         cleaned_col = _cols

#         if len(_cols) > 0: print(_cols)

#         # Assign cleaned <span> vals (which include, individually, titles, col heads, col vals)
#         col_vals_final.append(_cols)



# print(col_vals_final)

# print()


# # Removing empty lists
# col_vals_final = [x for x in col_vals_final if x != []]


# # Final set of titles
# title_final = []
# # Final set of col values
# clean_cols = []
# # Final set of footnotes
# ft_final = []

# parent_table = []

# # Looping through cleaned <span> vals 
# for i in range(1, len(col_vals_final) - 1):

#     # Getting title
#     if col_vals_final[i][0] == '(1)':
#         title_final.append(col_vals_final[i-1][0])

#     ## FOR EACH TITLE WE WILL HAVE A TABLE
#     #### WHERE EACH TABLE IS A COLLECTION OF COL HEADERS, COL VALUES

#     # Handling col value merging (2nd to last and last row are split off)
#     ## Getting 2nd to last row
#     if len(col_vals_final[i]) > 1 \
#     and (col_vals_final[i+1][0].lower() == 'total'\
#         or col_vals_final[i+1][0].replace(',', '').replace('.', '').replace(' - ', '').isdigit()):
#         # print('IN IF STATEMENT')
#         # print(col_vals_final[i])
#         # print(col_vals_final[i+1])
        
#         ## Getting last row, if it is split off (which it may not be)
#         if col_vals_final[i+2][0].lower() == 'total'\
#         or col_vals_final[i+1][0].replace(',', '').replace('.', '').replace(' - ', '').isdigit():
#             clean_cols.append(col_vals_final[i] + col_vals_final[i+1] + col_vals_final[i+2])

#         else:
#             clean_cols.append(col_vals_final[i] + col_vals_final[i+1])

    
#     # Getting footnote
#     if '(1)' in col_vals_final[i][0] \
#     and col_vals_final[i][0] != '(1)':
#         ft_final.append(col_vals_final[i][0])

    
#     # Since tables are not explicitly seperated in HTML output of pdf,
#     ## Splitting by KNOWN number of cols such that we get a list of lists,
#     ### where each sub list is a list of cols, which will compose the corresponding df output

#     ### SOMETHING WRONG HERE

#     # if len(clean_cols) > 1 \
#     # and len(clean_cols) % 4 == 0:
#     #     parent_table.append(clean_cols)
#     #     clean_cols = []


# # print(title_final)
# # print()
# # print(clean_cols)
# # print()
# # print(ft_final)

# for i in clean_cols:
#     print(i)
#     print()


# final_df = []
# # Looping through collected titles, tables, footnotes
# for title, df, footnote in zip(title_final, parent_table, ft_final):

#     print(title)
#     print(df)
#     print(pd.DataFrame(df).T)
#     print(footnote)
#     print()
#     print()

#     # Append list of [title, df, footnote(s)]
#     final_df.append(
#                         [title,
#                         pd.DataFrame(data = parent_table,
#                                      columns = ['', '# of Mtg Loans', 'Agg $ Outstanding', 'Agg % outstanding']),
#                         footnote]
#                     )
    


# print(final_df)
