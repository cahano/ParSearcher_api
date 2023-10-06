from typing import List, Dict, Any
from functools import lru_cache

"""
    Static values, hardcoded lists, etc that we care about
"""


# A temporary list of unique tags we want to look for
TEMP_UNIQUE_TAGS_LIST = ["annex", ""] 

# maintain a list of unique tags to help us extract data we want
@lru_cache
def unique_tag_list() -> List[str]: 
    return [t.lower() for t in TEMP_UNIQUE_TAGS_LIST]