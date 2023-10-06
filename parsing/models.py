import logging
import uuid
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

"""
Help us define what a PDF is and what a correct schema is by setting guidlines for extracted data
Currently use the PPM schema as starting point and generalize as we go
If we ever build ML models based on what clients want we can add/remove as we go
"""

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

@dataclass
class MortgageStatistics:

    headers_dataset: List[Dict[str, List[Any]]]

    # doesn't always exist
    pool_id: Optional[str] = None


@dataclass 
class Annex:

    annex_id: str
    
    # each annex section has a list of table headers we want to pull from
    # ex: "Mortgage Pool", "Index" - we should be able to find these programatically
    headers_dataset: List[Dict[str, List[Any]]]

@dataclass 
class PPM_Schema:
    """
        Generic schema for PPM requests
    """

    # let's assume for now every ppm will have an annex list
    # and a mortgage statistics list
    annex_list: List[Annex]
    mortgage_statistics: List[MortgageStatistics]


@dataclass 
class Page:
    """
        What's a page? This is a page
    """
    page_id: str
    # not sure what I want to limit this down to yet
    page_contents: Union[str, dict, PPM_Schema]

    @property
    def page_len(self) -> Optional[str]:
        if isinstance(self.page_contents, str):
            return len(str)        
        log.warn(f"Page {self.page_id} is not string, can't get keys")


@dataclass
class PDF:

    name: str
    # have a unique identifier for each parsed PDF object
    id = uuid.uuid4()
    request_id: str
    create_date: str    # datetime iso format
    pages: Optional[List[Page]]
    
    #schemas: List[Union[PPM_Schema]]
    schemas: Optional[List[PPM_Schema]]

    metadata: Optional[Dict[Any, Any]]

    @property
    def total_pages(self) -> Optional[int]:
        if not self.pages:
            log.error(f"No pages set in PDF object {self.id}")
            return None
        
        return len(self.pages)
    
    @property
    def get_page_strings(self) -> str:
        text: str = ""
        for page in self.pages:
            if isinstance(page.page_contents, str):
                text += page.page_contents
        # TODO add error logging for user 
        # lazy right now, will add it later 

        return text