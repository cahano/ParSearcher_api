#####################################################################
### Regex/search logic for various business cases (e.g. RMBS)
### 10/5/2023
### Is imported and used in vanillot_v1.py
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


# ADDITIONAL BUSINESS' PDF SEARCH LOGIC WILL GO HERE (IN THEORY)
