#####################################################################
### Input business logic for PDF page scan
### 12/26/2023
### Constant regex logic for RMBS (+ more soon)
#####################################################################

from enum import StrEnum


class RMBSLogic(StrEnum):
    '''
    Collection of Regex search strings for RMBS PPM docs
    '''

    term_sheet_start = r'GLOSSARY OF DEFINED TERMS'
    term_sheet_end = r'Annex A'

    annex_start = r'Annex A'
    annex_end = r'Annex [BCD][-][1]'


# ADDITIONAL BUSINESS' PDF SEARCH LOGIC WILL GO HERE


